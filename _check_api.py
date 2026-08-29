# -*- coding: utf-8 -*-
import io, sys, paramiko
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

def run(cmd):
    print(f'\n=== {cmd} ===')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8','replace'))

# 检查后端 API 返回的前2条数据，看中文是否正常
run('curl -s http://127.0.0.1:8000/detection/ | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d[\'data\'][:2], ensure_ascii=False, indent=2))"')

# 检查统计
run('curl -s http://127.0.0.1:8000/statistics/overview')

# 检查前端页面的 charset
run('head -10 /home/ubuntu/ginseng-project/ginseng-fronted/query.html')

ssh.close()
