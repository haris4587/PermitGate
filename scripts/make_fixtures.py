"""Create synthetic fixtures; accepts a public account address and Unix base time."""
import hashlib
import json
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
account = sys.argv[1] if len(sys.argv) > 1 else '0x' + '1' * 40
now = int(sys.argv[2]) if len(sys.argv) > 2 else 1795431600
policy = {'site':'SYNTHETIC Plant A / Bay 4','task_type':'Demonstration hot work','procedure':'HW-04: isolate energy, inspect equipment, verify welder qualification and assign a fire watch before welding.',
 'operator':account,'approvals':[{'role':'Permit issuer','account':account}],
 'requirements':[
 {'id':'isolation','kind':'procedure','subject':'Bay 4 isolation','rule':'Energy isolation completed and fire watch assigned under HW-04.','critical':True},
 {'id':'welder','kind':'qualification','subject':'Worker DEMO-01','rule':'Current hot-work training for DEMO-01.','critical':True},
 {'id':'equipment','kind':'equipment','subject':'Welder EQ-04','rule':'Pre-use inspection of EQ-04 passed with no unresolved defects.','critical':True},
 {'id':'briefing','kind':'procedure','subject':'Briefing register','rule':'Optional supplementary briefing attendance recorded.','critical':False}],
 'max_duration_seconds':28800,'max_document_age_seconds':2592000,'separate_duties':False}
start,end,issued,expiry = now+86400, now+100800, now-3600, now+172800
quotes = {'isolation':'Energy isolation completed and fire watch assigned under HW-04.',
 'welder':'Worker DEMO-01 has current hot-work training.',
 'equipment':'Welder EQ-04 pre-use inspection passed with no unresolved defects.',
 'briefing':'Optional supplementary briefing attendance recorded.'}
evidence = '\n'.join(['SYNTHETIC DEMONSTRATION ONLY. No real work is authorized.',
 'Permit DEMO-HW-001; site SYNTHETIC Plant A / Bay 4; task Demonstration hot work.',
 f'Work interval Unix seconds: start {start}, end {end}. Procedure HW-04.',
 *[f'Record {rid}: issued_at {issued}, expires_at {expiry}.' for rid in quotes],*quotes.values()])
bundle={'permit_id':'DEMO-HW-001','site':policy['site'],'task_type':policy['task_type'],'work_start':start,'work_end':end,
 'evidence':evidence,'evidence_sha256':hashlib.sha256(evidence.encode()).hexdigest(),'evidence_bytes':len(evidence.encode()),
 'records':[{'requirement_id':rid,'issued_at':issued,'expires_at':expiry} for rid in quotes]}
review = {rid:{'status':'SUPPORTED','quote':quote} for rid,quote in quotes.items()}
for name,obj in [('policy.json',policy),('bundle.json',bundle),('review.mock.json',review)]:
 (root/'fixtures'/name).write_text(json.dumps(obj,indent=2)+'\n')
print(hashlib.sha256(json.dumps(bundle,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest())
