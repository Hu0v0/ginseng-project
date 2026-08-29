# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=60)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8','replace')
    err = stderr.read().decode('utf-8','replace')
    print(f'$ {cmd}\n{out}{err}')

run('ps aux | grep "docker compose" | grep -v grep')
run('echo "Huhuiyan0320" | sudo -S docker images 2>&1')
run('echo "Huhuiyan0320" | sudo -S docker ps -a 2>&1')
run('tail -40 /tmp/build.log 2>&1')

ssh.close()
