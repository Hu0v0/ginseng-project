# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=60)

def run(cmd, t=60):
    print(f'\n$ {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t)
    out = stdout.read().decode('utf-8','replace')
    err = stderr.read().decode('utf-8','replace')
    if out: print(out)
    if err: print('[stderr]', err)
    print(f'[exit={stdout.channel.recv_exit_status()}]')

# 1. 用 nohup 在服务器后台启动，不依赖 SSH
run('cd ~/ginseng-project && echo "Huhuiyan0320" | sudo -S bash -c \'nohup docker compose up -d --build > /tmp/build.log 2>&1 & echo PID=$!\'')

# 2. 等 5 秒，确认进程在跑
time.sleep(5)
run('ps aux | grep "docker compose" | grep -v grep')
run('cat /tmp/build.log 2>&1 | head -30')

ssh.close()
print('\n=== 已在服务器后台启动，构建日志在 /tmp/build.log ===')
