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
    print(f'[exit={stdout.channel.recv_exit_status()}]')

# 先确认网络和 git
run('git --version')
run('curl -sI https://github.com 2>&1 | head -3')
# 直接 clone，显示完整输出
run('cd ~ && git clone --depth 1 --branch main https://github.com/Hu0v0/ginseng-project.git 2>&1', t=300)
run('ls -la ~/ginseng-project/ 2>&1 | head -20')

ssh.close()
