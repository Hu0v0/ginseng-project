# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = '81.68.167.116'
USER = 'ubuntu'
PWD = 'Huhuiyan0320'

def run(ssh, cmd, timeout=300):
    print(f'\n$ {cmd[:120]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout, get_pty=True)
    # 发送 sudo 密码
    stdin.write(PWD + '\n')
    stdin.flush()
    out = ''
    err = ''
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            chunk = stdout.channel.recv(4096).decode('utf-8', errors='replace')
            out += chunk
            print(chunk, end='')
        if stdout.channel.recv_stderr_ready():
            chunk = stdout.channel.recv_stderr(4096).decode('utf-8', errors='replace')
            err += chunk
        time.sleep(0.1)
    # 读取剩余
    while stdout.channel.recv_ready():
        chunk = stdout.channel.recv(4096).decode('utf-8', errors='replace')
        out += chunk
        print(chunk, end='')
    rc = stdout.channel.recv_exit_status()
    print(f'\n[exit={rc}]')
    return rc, out, err

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PWD, timeout=30)
print('登录成功')

# 1. 测试 sudo
rc, out, err = run(ssh, 'sudo -S whoami', timeout=30)
if 'root' not in out:
    print('sudo 失败，退出')
    ssh.close()
    sys.exit(1)

# 2. 安装 Docker 依赖和源
run(ssh, 'sudo -S apt-get update -qq', timeout=180)
run(ssh, 'sudo -S apt-get install -y -qq ca-certificates curl gnupg lsb-release', timeout=120)
run(ssh, 'sudo -S install -m 0755 -d /etc/apt/keyrings', timeout=30)
run(ssh, 'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo -S gpg --dearmor -o /etc/apt/keyrings/docker.gpg', timeout=60)
run(ssh, 'sudo -S chmod a+r /etc/apt/keyrings/docker.gpg', timeout=30)
run(ssh, 'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo -S tee /etc/apt/sources.list.d/docker.list', timeout=30)
run(ssh, 'sudo -S apt-get update -qq', timeout=120)

# 3. 安装 Docker
run(ssh, 'sudo -S apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin', timeout=300)

# 4. 验证
run(ssh, 'sudo -S docker --version', timeout=30)
run(ssh, 'sudo -S docker compose version', timeout=30)

# 5. 把 ubuntu 加入 docker 组
run(ssh, 'sudo -S usermod -aG docker ubuntu', timeout=30)

# 6. 安装 git
run(ssh, 'sudo -S apt-get install -y -qq git', timeout=60)
run(ssh, 'git --version', timeout=30)

ssh.close()
print('\n=== Docker + Git 安装完成 ===')
