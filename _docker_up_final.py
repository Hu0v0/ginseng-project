# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

cmd = 'cd ~/ginseng-project && echo "Huhuiyan0320" | sudo -S docker compose up -d --build 2>&1'
print(f'$ {cmd}')

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=900)

# 实时轮询读取，避免缓冲区满
while not stdout.channel.exit_status_ready():
    while stdout.channel.recv_ready():
        data = stdout.channel.recv(4096).decode('utf-8', errors='replace')
        print(data, end='')
    while stderr.channel.recv_ready():
        data = stderr.channel.recv(4096).decode('utf-8', errors='replace')
        print(data, end='')
    time.sleep(0.5)

# 读取剩余
while stdout.channel.recv_ready():
    print(stdout.channel.recv(4096).decode('utf-8', errors='replace'), end='')
while stderr.channel.recv_ready():
    print(stderr.channel.recv(4096).decode('utf-8', errors='replace'), end='')

rc = stdout.channel.recv_exit_status()
print(f'\n[exit={rc}]')

# 查看容器
print('\n=== docker ps -a ===')
stdin2, stdout2, stderr2 = ssh.exec_command('echo "Huhuiyan0320" | sudo -S docker ps -a 2>&1', timeout=30)
print(stdout2.read().decode('utf-8','replace'))

ssh.close()
print('\n=== DONE ===')
