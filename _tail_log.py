# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=120, banner_timeout=60, auth_timeout=60)

stdin, stdout, stderr = ssh.exec_command('tail -50 /tmp/build.log 2>&1; echo "---SEPARATOR---"; ps aux | grep "docker compose" | grep -v grep | wc -l', timeout=120)
out = stdout.read().decode('utf-8','replace')
print(out)

ssh.close()
