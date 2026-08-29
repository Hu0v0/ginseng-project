# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

def run(cmd, t=180):
    print(f'\n$ {cmd[:120]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t, get_pty=True)
    stdin.write('Huhuiyan0320\n'); stdin.flush()
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            print(stdout.channel.recv(4096).decode('utf-8','replace'), end='')
        time.sleep(0.1)
    while stdout.channel.recv_ready():
        print(stdout.channel.recv(4096).decode('utf-8','replace'), end='')
    print(f'\n[exit={stdout.channel.recv_exit_status()}]')

# 1. 杀掉可能残留的 docker compose，删掉不完整的仓库
run('pkill -f "docker compose" 2>/dev/null; sleep 2; rm -rf ~/ginseng-project; echo CLEANED')

# 2. 干净克隆，明确指定 main 分支
run('cd ~ && git clone --depth 1 --branch main https://github.com/Hu0v0/ginseng-project.git', t=180)

# 3. 确认文件
run('ls -la ~/ginseng-project/')
run('ls ~/ginseng-project/docker-compose.yml ~/ginseng-project/ginseng-backend/Dockerfile ~/ginseng-project/ginseng-fronted/index.html && echo FILES_OK')

# 4. 后台启动 docker compose build
run('cd ~/ginseng-project && echo "Huhuiyan0320" | sudo -S bash -c "nohup docker compose up -d --build > /tmp/build.log 2>&1 &" && sleep 5 && echo BUILD_LAUNCHED')

# 5. 确认在运行
run('ps aux | grep "docker compose" | grep -v grep')
run('tail -15 /tmp/build.log 2>&1')

ssh.close()
print('\n=== 构建已在服务器后台启动 ===')
