# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

def run(cmd, t=600):
    print(f'\n$ {cmd[:120]}')
    # 不用 get_pty，直接管道输入 sudo 密码
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t)
    out = stdout.read().decode('utf-8','replace')
    err = stderr.read().decode('utf-8','replace')
    if out: print(out)
    if err: print('[stderr]', err)
    rc = stdout.channel.recv_exit_status()
    print(f'[exit={rc}]')
    return rc

# 1. 测试 sudo（非 pty 模式）
run('echo "Huhuiyan0320" | sudo -S docker version 2>&1 | head -8')

# 2. 查看 docker-compose.yml
run('cat ~/ginseng-project/docker-compose.yml')

# 3. 启动构建
run('cd ~/ginseng-project && echo "Huhuiyan0320" | sudo -S docker compose up -d --build 2>&1', t=600)

ssh.close()
print('\n=== DONE ===')
