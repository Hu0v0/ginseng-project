# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

# 上传 main.py
sftp = ssh.open_sftp()
sftp.put(r'D:\ginseng-project\ginseng-backend\main.py', '/home/ubuntu/ginseng-project/ginseng-backend/main.py')
sftp.close()
print('main.py 已上传')

# 重启后端容器
stdin, stdout, stderr = ssh.exec_command('echo "Huhuiyan0320" | sudo -S docker restart ginseng-backend', timeout=60)
print(stdout.read().decode())
print('后端已重启')

time.sleep(8)

# 验证
stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8000/statistics/overview', timeout=30)
print('统计结果:', stdout.read().decode())

ssh.close()
print('完成')
