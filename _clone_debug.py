# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

def run(cmd, t=300):
    print(f'\n$ {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t)
    out = stdout.read().decode('utf-8','replace')
    err = stderr.read().decode('utf-8','replace')
    if out: print(out)
    if err: print('[stderr]', err)
    rc = stdout.channel.recv_exit_status()
    print(f'[exit={rc}]')
    return rc

# 1. 测试 GitHub 连通性
run('curl -sI --max-time 10 https://github.com 2>&1 | head -5')
run('git ls-remote https://github.com/Hu0v0/ginseng-project.git 2>&1 | head -3')

# 2. 干净 clone，显示进度
run('cd ~ && rm -rf ginseng-project && git clone --depth 1 --branch main --progress https://github.com/Hu0v0/ginseng-project.git 2>&1', t=300)

# 3. 确认
run('ls ~/ginseng-project/docker-compose.yml ~/ginseng-project/ginseng-backend/Dockerfile ~/ginseng-project/ginseng-fronted/index.html 2>&1')
run('du -sh ~/ginseng-project/ 2>&1')

ssh.close()
print('\n=== DONE ===')
