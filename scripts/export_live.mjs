// Read-only verifier. Requires a completed evidence/deployment.json; no wallet secrets.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import {TransactionHashVariant} from 'genlayer-js/types';
const d=JSON.parse(fs.readFileSync('evidence/deployment.json','utf8'));
if(d.status!=='deployed'||!d.address) throw Error('No verified deployment recorded');
const c=createClient({chain:studionet});
const read=async(fn,args=[])=>JSON.parse(await c.readContract({address:d.address,functionName:fn,args,transactionHashVariant:TransactionHashVariant.LATEST_FINAL}));
const local=fs.readFileSync('contracts/permit_gate.py');
const code=await c.getContractCode(d.address);
const remote=code.startsWith('0x')?Buffer.from(code.slice(2),'hex'):Buffer.from(code);
if(!remote.equals(local)) throw Error('Deployed source mismatch');
const transactions=[];
for(const tx of d.transactions){
 const r=await c.getTransaction({hash:tx.hash});
 if((r.statusName??r.status_name)!=='FINALIZED'||r.result_name!=='MAJORITY_AGREE'||r.leader_only!==false||!r.consensus_data?.leader_receipt?.some(x=>x.execution_result==='SUCCESS'))throw Error(`Unverified transaction: ${tx.action}`);
 transactions.push({action:tx.action,hash:tx.hash,status:'FINALIZED',result:r.result_name,leader_only:r.leader_only,votes:r.consensus_data.votes});
}
const state=await read('get_status'), events=[];
for(let i=1;i<=state.events;i++)events.push(await read('get_event',[i]));
const policy=await read('get_policy');
const assessment=await read('get_receipt',[d.permit_id??'DEMO-HW-001']);
const effective=await read('effective_status',[d.permit_id??'DEMO-HW-001']);
fs.writeFileSync('evidence/assessment-live.json',JSON.stringify(assessment,null,2)+'\n');
fs.writeFileSync('evidence/effective-live.json',JSON.stringify(effective,null,2)+'\n');
fs.writeFileSync('evidence/policy-live.json',JSON.stringify(policy,null,2)+'\n');
fs.writeFileSync('evidence/events-live.json',JSON.stringify(events,null,2)+'\n');
fs.writeFileSync('evidence/verified-live.json',JSON.stringify({source_matches:true,source_sha256:crypto.createHash('sha256').update(local).digest('hex'),state,transactions,assessment_outcome:assessment.data.result.outcome,effective_status:effective},null,2)+'\n');
console.log('Source and finalized full-consensus transactions verified. Run python scripts/verify_chain.py evidence/events-live.json');
