"""Use the existing Git credential manager without writing or printing tokens."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
OWNER='carloxorjuela'
NAME='crecere-ai-call-analysis'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--publish',action='store_true')
    args=parser.parse_args()
    env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never')
    credential=subprocess.run(['git','credential','fill'],input=f'protocol=https\nhost=github.com\nusername={OWNER}\n\n',text=True,capture_output=True,env=env,cwd=ROOT)
    if credential.returncode:
        raise SystemExit('No usable GitHub credential. Authenticate via Git Credential Manager.')
    fields=dict(line.split('=',1) for line in credential.stdout.splitlines() if '=' in line)
    token=fields.get('password')
    if not token:
        raise SystemExit('Credential manager returned no token.')
    def request(path,payload=None):
        req=Request('https://api.github.com'+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'crecere-analysis','Content-Type':'application/json'})
        try:
            with urlopen(req,timeout=30) as response:
                return response.status,json.load(response)
        except HTTPError as exc:
            return exc.code,{}
    status,user=request('/user')
    if status!=200 or user.get('login','').lower()!=OWNER:
        raise SystemExit(f'GitHub account verification failed (HTTP {status}).')
    print('Authenticated GitHub account:',user['login'])
    status,repo=request(f'/repos/{OWNER}/{NAME}')
    print('Repository lookup HTTP:',status)
    if not args.publish:
        return
    tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
    if not (ROOT/'report.html').is_file() or not (ROOT/'data/analytic.csv').is_file():
        raise SystemExit('Publication blocked: final report or analytical table missing.')
    banned=('data/private/','audios_prueba_data_analyst/','.venv/','.cache/')
    if any(p.startswith(banned) or p.endswith(('.wav','.env')) for p in tracked):
        raise SystemExit('Publication blocked: private file tracked.')
    if status==404:
        status,repo=request('/user/repos',{'name':NAME,'description':'Comparación auditable de gestiones humanas e IA: prueba técnica Creceré AI.','private':False,'auto_init':False})
        if status!=201:
            raise SystemExit(f'Repository creation failed (HTTP {status}).')
    elif status!=200:
        raise SystemExit(f'Repository lookup failed (HTTP {status}).')
    if repo.get('private'):
        raise SystemExit('Existing repository is private; visibility was not changed.')
    remote=repo['clone_url']
    existing=subprocess.run(['git','remote','get-url','origin'],cwd=ROOT,text=True,capture_output=True)
    if existing.returncode:
        subprocess.run(['git','remote','add','origin',remote],cwd=ROOT,check=True)
    elif existing.stdout.strip()!=remote:
        raise SystemExit('Existing origin differs; not changed.')
    subprocess.run(['git','push','-u','origin','HEAD:main'],cwd=ROOT,check=True,env=env)
    print('Published:',repo['html_url'])


if __name__=='__main__':
    main()
