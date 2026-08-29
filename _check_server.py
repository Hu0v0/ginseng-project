# -*- coding: utf-8 -*-
import io, sys, paramiko
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

def run(cmd):
    print(f'\n=== {cmd} ===')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8','replace'))
    err = stderr.read().decode('utf-8','replace')
    if err: print('[stderr]', err)

run('echo "Huhuiyan0320" | sudo -S docker ps -a 2>&1')
run('echo "Huhuiyan0320" | sudo -S docker logs ginseng-backend --tail 15 2>&1')
run('grep CLOUD_API /home/ubuntu/ginseng-project/ginseng-fronted/js/api-config.js')
run('curl -s http://127.0.0.1:8000/statistics/overview')
run('curl -s -o /dev/null -w "frontend: %{http_code}\n" http://127.0.0.1/')

ssh.close()
