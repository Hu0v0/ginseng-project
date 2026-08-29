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

run(ssh, 'ls -la ~/ginseng-project/ 2>&1 | head -20', timeout=30)
run(ssh, 'sudo -S docker ps -a 2>&1', timeout=60)
run(ssh, 'sudo -S docker compose -f ~/ginseng-project/docker-compose.yml ps 2>&1', timeout=60)
run(ssh, 'curl -s http://127.0.0.1:8000/ 2>&1', timeout=30)
run(ssh, 'curl -s -o /dev/null -w "frontend http_code: %{http_code}\n" http://127.0.0.1:80/ 2>&1', timeout=30)

ssh.close()
