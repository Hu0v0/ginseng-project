# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

def run(cmd, t=180):
    print(f'\n$ {cmd[:100]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t, get_pty=True)
    stdin.write('Huhuiyan0320\n'); stdin.flush()
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            print(stdout.channel.recv(4096).decode('utf-8','replace'), end='')
        time.sleep(0.1)
    while stdout.channel.recv_ready():
        print(stdout.channel.recv(4096).decode('utf-8','replace'), end='')
    print(f'\n[exit={stdout.channel.recv_exit_status()}]')

# 1. 删掉不完整的
run('rm -rf ~/ginseng-project && echo REMOVED')

# 2. 干净克隆 main 分支
run('cd ~ && git clone --depth 1 --branch main https://github.com/Hu0v0/ginseng-project.git', t=180)

# 3. 确认关键文件
run('ls ~/ginseng-project/docker-compose.yml ~/ginseng-project/ginseng-backend/Dockerfile ~/ginseng-project/ginseng-fronted/index.html')

# 4. 直接启动（-d 后台运行容器，命令会立即返回）
run('cd ~/ginseng-project && echo "Huhuiyan0320" | sudo -S docker compose up -d --build', t=600)

# 5. 查看容器
time.sleep(10)
run('echo "Huhuiyan0320" | sudo -S docker ps -a')

ssh.close()
print('\n=== DONE ===')
