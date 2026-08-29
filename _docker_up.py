# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

def run(cmd, t=600):
    print(f'\n$ {cmd[:120]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t, get_pty=True)
    stdin.write('Huhuiyan0320\n'); stdin.flush()
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            print(stdout.channel.recv(4096).decode('utf-8','replace'), end='')
        time.sleep(0.2)
    while stdout.channel.recv_ready():
        print(stdout.channel.recv(4096).decode('utf-8','replace'), end='')
    rc = stdout.channel.recv_exit_status()
    print(f'\n[exit={rc}]')

# 启动构建
run('cd ~/ginseng-project && echo "Huhuiyan0320" | sudo -S docker compose up -d --build 2>&1', t=600)

# 查看容器
time.sleep(15)
run('echo "Huhuiyan0320" | sudo -S docker ps -a 2>&1')

# 后端日志
run('echo "Huhuiyan0320" | sudo -S docker logs ginseng-backend --tail 30 2>&1')

# 测试
run('curl -s http://127.0.0.1:8000/ 2>&1')
run('curl -s http://127.0.0.1:8000/statistics/overview 2>&1')
run('curl -s -o /dev/null -w "frontend: %{http_code}\n" http://127.0.0.1:80/ 2>&1')

ssh.close()
print('\n=== DONE ===')
