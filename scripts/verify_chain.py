"""Verify canonical SHA-256 receipts exported as a JSON array; no RPC or wallet."""
import hashlib
import json
import sys

def verify(events):
    previous = '0' * 64
    domain = None
    for index, event in enumerate(events,1):
        body = dict(event)
        claimed = body.pop('event_hash')
        assert body['sequence'] == index, 'sequence gap'
        assert body['previous_hash'] == previous, 'broken chain'
        actual_domain=(body['chain_id'],body['contract'],body['policy_hash'])
        if domain is None: domain=actual_domain
        assert domain == actual_domain, 'domain changed'
        encoded=json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
        assert hashlib.sha256(encoded).hexdigest() == claimed, 'hash mismatch'
        previous = claimed
    return previous

if __name__=='__main__':
    with open(sys.argv[1]) as f: events=json.load(f)
    print(f'Verified {len(events)} events; head {verify(events)}')
