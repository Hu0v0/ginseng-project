# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

def run(cmd, t=600):
    print(f'\n=== {cmd[:150]} ===')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t)
    out = stdout.read().decode('utf-8','replace')
    err = stderr.read().decode('utf-8','replace')
    if out: print(out)
    if err: print('[stderr]', err)
    rc = stdout.channel.recv_exit_status()
    print(f'[exit={rc}]')
    return rc

# 1. 看配置
run('cat ~/ginseng-project/docker-compose.yml')

# 2. 验证配置
run('cd ~/ginseng-project && echo "Huhuiyan0320" | sudo -S docker compose config 2>&1')

# 3. 看 Dockerfile
run('cat ~/ginseng-project/ginseng-backend/Dockerfile')

ssh.close()
