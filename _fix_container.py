# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

def run(cmd, t=60):
    print(f'\n$ {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t)
    print(stdout.read().decode('utf-8','replace'))
    err = stderr.read().decode('utf-8','replace')
    if err: print('[stderr]', err)

# 进入容器修改标准限值
run('echo "Huhuiyan0320" | sudo -S docker exec ginseng-backend sed -i \'s/"lead": 0.05/"lead": 5.0/; s/"arsenic": 0.02/"arsenic": 2.0/; s/"cadmium": 0.01/"cadmium": 0.3/; s/"mercury": 0.01/"mercury": 0.2/\' /app/main.py')

# 确认修改
run('echo "Huhuiyan0320" | sudo -S docker exec ginseng-backend grep -A5 "HEAVY_METAL_STANDARD" /app/main.py')

# 重启后端
run('echo "Huhuiyan0320" | sudo -S docker restart ginseng-backend')
time.sleep(8)

# 验证
run('curl -s http://127.0.0.1:8000/statistics/overview')

ssh.close()
print('\n完成')
