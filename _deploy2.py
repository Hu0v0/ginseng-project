# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = '81.68.167.116'
USER = 'ubuntu'
PWD = 'Huhuiyan0320'

def run(ssh, cmd, timeout=300):
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

# 1. 清理之前失败的配置
run(ssh, 'sudo -S rm -f /etc/apt/sources.list.d/docker.list /etc/apt/keyrings/docker.gpg', timeout=30)

# 2. 用腾讯云镜像源添加 GPG key
run(ssh, 'curl -fsSL https://mirrors.cloud.tencent.com/docker-ce/linux/ubuntu/gpg | sudo -S gpg --dearmor -o /etc/apt/keyrings/docker.gpg', timeout=60)

# 3. 添加腾讯云 Docker 源
run(ssh, 'echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.cloud.tencent.com/docker-ce/linux/ubuntu jammy stable" | sudo -S tee /etc/apt/sources.list.d/docker.list', timeout=30)

# 4. apt update
run(ssh, 'sudo -S apt-get update -qq', timeout=120)

# 5. 安装 Docker
run(ssh, 'sudo -S apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin', timeout=300)

# 6. 配置 Docker 镜像加速器（中科大公共镜像）
run(ssh, '''sudo -S mkdir -p /etc/docker && sudo -S tee /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn", "https://hub-mirror.c.163.com"]
}
EOF''', timeout=30)

# 7. 启动 Docker
run(ssh, 'sudo -S systemctl daemon-reload', timeout=30)
run(ssh, 'sudo -S systemctl enable docker', timeout=30)
run(ssh, 'sudo -S systemctl start docker', timeout=30)

# 8. 验证
run(ssh, 'sudo -S docker --version', timeout=30)
run(ssh, 'sudo -S docker compose version', timeout=30)
run(ssh, 'sudo -S docker info 2>&1 | grep -A2 "Registry Mirrors"', timeout=30)

# 9. ubuntu 加入 docker 组
run(ssh, 'sudo -S usermod -aG docker ubuntu', timeout=30)

ssh.close()
print('\n=== Docker 安装完成 ===')
