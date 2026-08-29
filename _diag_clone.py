# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = '81.68.167.116'
USER = 'ubuntu'
PWD = 'Huhuiyan0320'

def run(ssh, cmd, timeout=120):
    print(f'\n$ {cmd}')
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

# 1. 查看远程分支
run(ssh, 'git ls-remote https://github.com/Hu0v0/ginseng-project.git', timeout=60)

# 2. 进入目录查看状态
run(ssh, 'cd ~/ginseng-project && git branch -a && git status && git log --oneline -3', timeout=30)

# 3. 尝试强制 checkout
run(ssh, 'cd ~/ginseng-project && git checkout -f main 2>&1', timeout=60)

# 4. 再次查看文件
run(ssh, 'ls -la ~/ginseng-project/', timeout=30)

ssh.close()
