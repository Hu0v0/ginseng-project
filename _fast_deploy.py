# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

def run(cmd, t=120):
    print(f'\n$ {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t, get_pty=True)
    stdin.write('Huhuiyan0320\n'); stdin.flush()
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            print(stdout.channel.recv(4096).decode('utf-8','replace'), end='')
        time.sleep(0.1)
    while stdout.channel.recv_ready():
        print(stdout.channel.recv(4096).decode('utf-8','replace'), end='')
    print(f'\n[exit={stdout.channel.recv_exit_status()}]')

# 直接拉取
run('cd ~/ginseng-project && git remote -v')
run('cd ~/ginseng-project && git fetch --depth 1 origin main:main 2>&1')
run('cd ~/ginseng-project && git checkout main 2>&1')
run('ls ~/ginseng-project/')
run('ls ~/ginseng-project/docker-compose.yml ~/ginseng-project/ginseng-backend/Dockerfile')

# 后台启动构建
run('cd ~/ginseng-project && echo "Huhuiyan0320" | sudo -S bash -c "nohup docker compose up -d --build > /tmp/build.log 2>&1 &" && sleep 3 && echo BUILD_STARTED')
run('ps aux | grep "docker compose" | grep -v grep')
run('tail -10 /tmp/build.log 2>&1')

ssh.close()
print('\n=== DONE ===')
