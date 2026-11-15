#!/usr/bin/env python3
"""Durable OneDev project plus Git push/clone product workflow."""
import base64,json,os,pathlib,secrets,subprocess,tempfile,urllib.request,urllib.error
base=os.environ.get('BASE_URL_ONEDEV',os.environ['BASE_URL']).rstrip('/')
user=os.environ.get('ONEDEV_USER','admin'); password=os.environ['ONEDEV_PASSWORD']
phase=os.environ['SMOKE_PHASE']; assert phase in ('boot','upgrade','redeploy'),phase
state=pathlib.Path(os.environ.get('SMOKE_STATE',os.path.join(os.environ.get('SUPERCOMPUTER_OUTPUT_DIR','.'),'smoke-state.json')))
def api(path,body=None,pw=password):
 headers={'Authorization':'Basic '+base64.b64encode((user+':'+pw).encode()).decode(),'Content-Type':'application/json'}
 request=urllib.request.Request(base+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
 try:
  with urllib.request.urlopen(request,timeout=60) as r: return r.status,json.load(r)
 except urllib.error.HTTPError as e: return e.code,None
assert api('/~api/projects?offset=0&count=1',pw='invalid-validation-password')[0] in (401,403),'invalid credentials accepted'
with tempfile.TemporaryDirectory() as tmp:
 tmp=pathlib.Path(tmp); askpass=tmp/'askpass.py';askpass.write_text('#!/usr/bin/env python3\nimport os,sys\nprint(os.environ["ONEDEV_USER"] if "Username" in sys.argv[1] else os.environ["ONEDEV_PASSWORD"])\n');askpass.chmod(0o700)
 env={**os.environ,'GIT_ASKPASS':str(askpass),'GIT_TERMINAL_PROMPT':'0','ONEDEV_USER':user,'ONEDEV_PASSWORD':password}
 def git(*args,cwd=None):
  result=subprocess.run(['git',*args],cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=120)
  assert result.returncode==0,'Git operation failed: '+str(args[0])
  return result.stdout.strip()
 if phase=='boot':
  assert not state.exists(),'boot must not overwrite existing seed evidence'
  seed={'name':'railway-proof-'+secrets.token_hex(5),'marker':secrets.token_hex(24)}
  status,data=api('/~api/projects',{'name':seed['name'],'description':seed['marker'],'codeManagement':True,'issueManagement':True,'codeIndexingSetting':{},'gitPackConfig':{}})
  assert status==200,'project creation failed: '+str(status)
  work=tmp/'seed';work.mkdir();git('init','-b','main',str(work));git('config','user.email','validation@example.invalid',cwd=work);git('config','user.name','Railway validation',cwd=work)
  (work/'proof.txt').write_text(seed['marker']+'\n');git('add','proof.txt',cwd=work);git('commit','-m','test: persistent repository marker',cwd=work)
  seed['commit']=git('rev-parse','HEAD',cwd=work);git('push',base+'/'+seed['name'],'main',cwd=work)
  state.parent.mkdir(parents=True,exist_ok=True);state.write_text(json.dumps(seed));state.chmod(0o600)
 else:
  assert state.exists(),'missing boot evidence: refusing to reseed after '+phase
  seed=json.loads(state.read_text())
 status,projects=api('/~api/projects?offset=0&count=100');assert status==200
 assert any(p.get('name')==seed['name'] and p.get('description')==seed['marker'] for p in projects),'persistent project missing'
 clone=tmp/'verify';git('clone','--quiet','--branch','main',base+'/'+seed['name'],str(clone))
 assert git('rev-parse','HEAD',cwd=clone)==seed['commit'],'persisted commit changed'
 assert (clone/'proof.txt').read_text()==seed['marker']+'\n','persisted Git marker missing'
print('PASS OneDev project API, denied credentials, Git marker persistence:',phase)
