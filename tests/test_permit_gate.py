from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = str(ROOT/'contracts/permit_gate.py')
NOW = 1795431600

def iso(t):
    return datetime.fromtimestamp(t,timezone.utc).isoformat()

def warp(vm,t):
    # gltest 0.29.2 warp updates datetime.now but leaves imported message_raw stale.
    # Refresh that public message field to model the next transaction's timestamp.
    vm.warp(iso(t))
    from genlayer import gl
    gl.message_raw['datetime']=iso(t)

def fixture(name):
    return json.loads((ROOT/'fixtures'/name).read_text())

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)

def sha(x):
    return hashlib.sha256(canon(x).encode()).hexdigest()

@pytest.fixture
def setup(direct_vm,direct_deploy,direct_owner):
    p=fixture('policy.json'); p['operator']='0x'+direct_owner.hex(); p['approvals'][0]['account']=p['operator']
    direct_vm.warp(iso(NOW))
    direct_vm.check_pickling=True
    c=direct_deploy(SOURCE,json.dumps(p),sdk_version='v0.2.16')
    b=fixture('bundle.json'); r=fixture('review.mock.json')
    direct_vm.mock_llm(r'^PERMITGATE_REVIEW:',json.dumps(r))
    direct_vm.mock_llm(r'^PERMITGATE_GROUNDING:','{"grounded":true}')
    return direct_vm,c,p,b,r

def lock(setup):
    return json.loads(setup[1].lock_permit(json.dumps(setup[3])))

def attest(setup,approved=True):
    return json.loads(setup[1].attest(setup[3]['permit_id'],sha(setup[3]),approved))

def evaluate(setup,approval=True):
    lock(setup)
    if approval: attest(setup)
    return json.loads(setup[1].evaluate(setup[3]['permit_id']))

def test_authorized_independent_validator(setup):
    event=evaluate(setup)
    assert event['data']['result']['outcome']=='AUTHORIZED'
    assert setup[0].run_validator() is True
    assert event.pop('event_hash')==sha(event)

def test_missing_approval(setup):
    assert evaluate(setup,False)['data']['result']['outcome']=='INCONCLUSIVE'

def test_rejected_approval(setup):
    lock(setup); attest(setup,False)
    assert json.loads(setup[1].evaluate(setup[3]['permit_id']))['data']['result']['outcome']=='VIOLATION'

@pytest.mark.parametrize('rid',['isolation','welder','equipment','briefing'])
@pytest.mark.parametrize('status',['CONTRADICTED','UNKNOWN'])
def test_requirement_outcomes(setup,rid,status):
    vm,c,p,b,r=setup; r[rid]['status']=status
    if status=='UNKNOWN': r[rid]['quote']=''
    vm.clear_mocks(); vm.mock_llm(r'^PERMITGATE_REVIEW:',json.dumps(r)); vm.mock_llm(r'^PERMITGATE_GROUNDING:','{"grounded":true}')
    outcome='INCONCLUSIVE' if status=='UNKNOWN' else 'CONDITIONAL' if rid=='briefing' else 'VIOLATION'
    assert evaluate(setup)['data']['result']['outcome']==outcome

@pytest.mark.parametrize('mutation',['sha','bytes','utf8_bytes','scope','future_issue','float_time','bool_time','order','missing','extra','empty','oversize','start','end'])
def test_reject_bad_bundle(setup,mutation):
    vm,c,p,b,r=setup
    if mutation=='sha': b['evidence_sha256']='f'*64
    elif mutation=='bytes': b['evidence_bytes']+=1
    elif mutation=='utf8_bytes':
        b['evidence']+=' é'; b['evidence_sha256']=hashlib.sha256(b['evidence'].encode()).hexdigest(); b['evidence_bytes']=len(b['evidence'])
    elif mutation=='scope': b['site']='other'
    elif mutation=='future_issue': b['records'][0]['issued_at']=NOW+1
    elif mutation=='float_time': b['records'][0]['issued_at']=float(NOW)
    elif mutation=='bool_time': b['work_start']=True
    elif mutation=='order': b['records'].reverse()
    elif mutation=='missing': b['records'].pop()
    elif mutation=='extra': b['extra']=1
    elif mutation=='empty': b['evidence']=' '
    elif mutation=='oversize': b['evidence']='a'*16001
    elif mutation=='start': b['work_start']=NOW
    elif mutation=='end': b['work_end']=b['work_start']+p['max_duration_seconds']+1
    with pytest.raises(Exception): lock(setup)

@pytest.mark.parametrize('field,value',[('operator','0x'+'0'*40),('separate_duties',1),('requirements',[]),('max_duration_seconds',True),('max_document_age_seconds',0),('procedure',' '),('approvals',[])])
def test_reject_bad_policy(direct_deploy,field,value):
    p=fixture('policy.json'); p[field]=value
    with pytest.raises(Exception): direct_deploy(SOURCE,json.dumps(p),sdk_version='v0.2.16')

def test_require_core_critical_categories(direct_deploy):
    p=fixture('policy.json'); p['requirements'][0]['critical']=False
    with pytest.raises(Exception): direct_deploy(SOURCE,json.dumps(p),sdk_version='v0.2.16')

def test_enforce_separate_duties(direct_deploy):
    p=fixture('policy.json'); p['separate_duties']=True
    with pytest.raises(Exception): direct_deploy(SOURCE,json.dumps(p),sdk_version='v0.2.16')

def test_duplicate_json_key(setup):
    raw=json.dumps(setup[3]); raw=raw[:-1]+',"permit_id":"replacement"}'
    with pytest.raises(Exception): setup[1].lock_permit(raw)

@pytest.mark.parametrize('mutation',['quote','markdown','extra','unknown_quote','invalid_status','llm_failure'])
def test_model_malformed_fails_closed(setup,mutation):
    vm,c,p,b,r=setup
    if mutation=='quote': r['isolation']['quote']='invented quotation'
    elif mutation=='extra': r['extra']={}
    elif mutation=='unknown_quote': r['welder']['status']='UNKNOWN'
    elif mutation=='invalid_status': r['welder']['status']='AUTHORIZED'
    raw='```'+json.dumps(r)+'```' if mutation=='markdown' else 'unavailable' if mutation=='llm_failure' else json.dumps(r)
    vm.clear_mocks(); vm.mock_llm(r'^PERMITGATE_REVIEW:',raw); vm.mock_llm(r'^PERMITGATE_GROUNDING:','{"grounded":true}')
    assert evaluate(setup)['data']['result']['outcome']=='INCONCLUSIVE'

def test_validator_disagrees_independently(setup):
    evaluate(setup); vm,c,p,b,r=setup; r['welder']={'status':'UNKNOWN','quote':''}
    vm.clear_mocks(); vm.mock_llm(r'^PERMITGATE_REVIEW:',json.dumps(r))
    assert vm.run_validator() is False

@pytest.mark.parametrize('audit',['{"grounded":false}','{"grounded":1}','{"grounded":true,"extra":0}','invalid'])
def test_validator_rejects_bad_grounding(setup,audit):
    evaluate(setup); vm,c,p,b,r=setup
    vm.clear_mocks(); vm.mock_llm(r'^PERMITGATE_REVIEW:',json.dumps(r)); vm.mock_llm(r'^PERMITGATE_GROUNDING:',audit)
    assert vm.run_validator() is False

@pytest.mark.parametrize('kind',['expiry','age'])
def test_validity_covers_entire_shift(setup,kind):
    vm,c,p,b,r=setup
    if kind=='expiry': b['records'][0]['expires_at']=b['work_end']-1
    else: b['records'][0]['issued_at']=b['work_end']-p['max_document_age_seconds']-1
    assert evaluate(setup)['data']['result']['outcome']=='VIOLATION'

def test_expiry_inclusive_boundary(setup):
    setup[3]['records'][0]['expires_at']=setup[3]['work_end']
    assert evaluate(setup)['data']['result']['outcome']=='AUTHORIZED'

def test_approvals_after_start_rejected(setup):
    lock(setup); warp(setup[0],setup[3]['work_start'])
    with pytest.raises(Exception): attest(setup)

def test_assessment_after_start_violation(setup):
    lock(setup); attest(setup); warp(setup[0],setup[3]['work_start'])
    assert json.loads(setup[1].evaluate(setup[3]['permit_id']))['data']['result']['outcome']=='VIOLATION'

def test_no_rewrite_reapproval_or_reroll(setup):
    evaluate(setup)
    for fn in [lambda:lock(setup),lambda:attest(setup),lambda:setup[1].evaluate(setup[3]['permit_id'])]:
        with pytest.raises(Exception): fn()

def test_wrong_attestation_hash(setup):
    lock(setup)
    with pytest.raises(Exception): setup[1].attest(setup[3]['permit_id'],'0'*64,True)

@pytest.mark.parametrize('method',['lock','attest','evaluate','stop'])
def test_unauthorized_account(setup,direct_alice,method):
    vm,c,p,b,r=setup
    if method!='lock': lock(setup)
    vm.sender=direct_alice
    with pytest.raises(Exception):
        if method=='lock': lock(setup)
        elif method=='attest': attest(setup)
        elif method=='evaluate': c.evaluate(b['permit_id'])
        else: c.stop_work(b['permit_id'],'unauthorized')

def test_approval_sequence_and_distinct_accounts(direct_vm,direct_deploy,direct_owner,direct_alice,direct_bob):
    p=fixture('policy.json'); p['operator']='0x'+direct_owner.hex()
    p['approvals']=[{'role':'Issuer','account':'0x'+direct_alice.hex()},{'role':'Safety officer','account':'0x'+direct_bob.hex()}]; p['separate_duties']=True
    direct_vm.warp(iso(NOW)); c=direct_deploy(SOURCE,json.dumps(p),sdk_version='v0.2.16'); b=fixture('bundle.json')
    c.lock_permit(json.dumps(b)); direct_vm.sender=direct_bob
    with pytest.raises(Exception): c.attest(b['permit_id'],sha(b),True)
    direct_vm.sender=direct_alice; c.attest(b['permit_id'],sha(b),True)
    direct_vm.sender=direct_bob; c.attest(b['permit_id'],sha(b),True)
    assert len(json.loads(c.get_permit(b['permit_id']))['approvals'])==2

def test_effective_window_expiry_stop_and_receipt_immutability(setup):
    vm,c,p,b,r=setup; receipt=evaluate(setup)
    assert json.loads(c.effective_status(b['permit_id']))['may_proceed'] is False
    warp(vm,b['work_start']); assert json.loads(c.effective_status(b['permit_id']))['may_proceed'] is True
    warp(vm,b['work_end']); assert json.loads(c.effective_status(b['permit_id']))['reason']=='expired'
    stop=json.loads(c.stop_work(b['permit_id'],'Demonstration stop'))
    assert json.loads(c.effective_status(b['permit_id']))['reason']=='stopped'
    assert json.loads(c.get_receipt(b['permit_id']))==receipt
    assert stop['previous_hash']==receipt['event_hash']
    with pytest.raises(Exception): c.stop_work(b['permit_id'],'again')

def test_stop_before_evaluation(setup):
    lock(setup); setup[1].stop_work(setup[3]['permit_id'],'Hazard reported')
    with pytest.raises(Exception): attest(setup)
    with pytest.raises(Exception): setup[1].evaluate(setup[3]['permit_id'])

def test_hash_chain_and_pagination_bounds(setup):
    evaluate(setup); c=setup[1]; previous='0'*64
    status=json.loads(c.get_status())
    for i in range(1,status['events']+1):
        event=json.loads(c.get_event(i)); assert event['previous_hash']==previous
        previous=event.pop('event_hash'); assert previous==sha(event)
    assert previous==status['head']
    for i in [0,4,-1,True]:
        with pytest.raises(Exception): c.get_event(i)
