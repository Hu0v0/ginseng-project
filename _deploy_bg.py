# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = '81.68.167.116'
USER = 'ubuntu'
PWD = 'Huhuiyan0320'

def run(ssh, cmd, timeout=180):
    print(f'\n$ {cmd[:120]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout, get_pty=True)
    stdin.write(PWD + '\n')
    stdin.flush()
    out = ''
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            chunk = stdout.channel.recv(4096).decode('utf-8', errors='replace')
            out += chunk
            print(chunk, end='')
        time.sleep(0.1)
    while stdout.channel.recv_ready():
        chunk = stdout.channel.recv(4096).decode('utf-8', errors='replace')
        out += chunk
        print(chunk, end='')
    rc = stdout.channel.recv_exit_status()
    print(f'\n[exit={rc}]')
    return rc, out

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PWD, timeout=30)
print('登录成功')

# 1. 修复 git，拉取文件
run(ssh, 'cd ~/ginseng-project && git fetch origin main && git checkout -B main origin/main', timeout=120)
run(ssh, 'ls ~/ginseng-project/docker-compose.yml ~/ginseng-project/ginseng-backend/Dockerfile ~/ginseng-project/ginseng-fronted/index.html', timeout=30)

# 2. 关键：用 nohup 在服务器后台启动 docker compose build，不依赖用户电脑
run(ssh, 'cd ~/ginseng-project && echo "Huhuiyan0320" | sudo -S nohup docker compose up -d --build > /tmp/ginseng_build.log 2>&1 & echo "BUILD_PID=$!"', timeout=30)

# 3. 确认进程在跑
time.sleep(5)
run(ssh, 'ps aux | grep "docker compose" | grep -v grep', timeout=30)
run(ssh, 'tail -20 /tmp/ginseng_build.log 2>&1', timeout=30)

ssh.close()
print('\n=== 服务器后台构建已启动 ===')
print('你可以充电了，构建在服务器上自己跑，不依赖你电脑')
