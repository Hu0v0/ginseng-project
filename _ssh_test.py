# -*- coding: utf-8 -*-
import io, sys, paramiko
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = '81.68.167.116'
USER = 'root'
PWD = 'Huhuiyan0320'

def run(ssh, cmd, timeout=120):
    print(f'\n$ {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    rc = stdout.channel.recv_exit_status()
    if out.strip():
        print(out.strip()[:2000])
    if err.strip():
        print('[stderr]', err.strip()[:500])
    print(f'[exit={rc}]')
    return rc, out, err

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f'连接 {USER}@{HOST} ...')
ssh.connect(HOST, username=USER, password=PWD, timeout=30)
print('登录成功！')

run(ssh, 'whoami && hostname')
run(ssh, 'cat /etc/os-release | head -5')
run(ssh, 'uname -a')
run(ssh, 'docker --version 2>&1 || echo "docker not installed"')
run(ssh, 'git --version 2>&1 || echo "git not installed"')
run(ssh, 'df -h / | tail -1')
run(ssh, 'free -h | head -2')

ssh.close()
print('\n=== 连接测试完成 ===')
