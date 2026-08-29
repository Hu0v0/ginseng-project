# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = '81.68.167.116'
USER = 'ubuntu'
PWD = 'Huhuiyan0320'

def run(ssh, cmd, timeout=600):
    print(f'\n$ {cmd[:150]}')
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

# 1. 拉代码
run(ssh, 'cd ~ && rm -rf ginseng-project && git clone https://github.com/Hu0v0/ginseng-project.git', timeout=120)
run(ssh, 'ls -la ~/ginseng-project/', timeout=30)

# 2. 构建并启动（用 sudo，因为当前会话 docker 组未生效）
run(ssh, 'cd ~/ginseng-project && sudo -S docker compose up -d --build', timeout=600)

# 3. 等待并查看容器状态
time.sleep(10)
run(ssh, 'sudo -S docker ps -a', timeout=60)

# 4. 查看后端日志
run(ssh, 'sudo -S docker logs ginseng-backend --tail 30 2>&1', timeout=60)

# 5. 本地测试后端
run(ssh, 'curl -s http://127.0.0.1:8000/ 2>&1', timeout=30)
run(ssh, 'curl -s http://127.0.0.1:8000/statistics/overview 2>&1', timeout=30)

# 6. 测试前端
run(ssh, 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/ 2>&1', timeout=30)

ssh.close()
print('\n=== 部署完成 ===')
