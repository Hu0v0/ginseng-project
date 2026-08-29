# -*- coding: utf-8 -*-
import io, sys, paramiko
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

sftp = ssh.open_sftp()
files = [
    (r'D:\ginseng-project\ginseng-fronted\query.html', '/home/ubuntu/ginseng-project/ginseng-fronted/query.html'),
    (r'D:\ginseng-project\ginseng-fronted\statistics.html', '/home/ubuntu/ginseng-project/ginseng-fronted/statistics.html'),
    (r'D:\ginseng-project\ginseng-fronted\admin.html', '/home/ubuntu/ginseng-project/ginseng-fronted/admin.html'),
]
for local, remote in files:
    sftp.put(local, remote)
    print(f'已上传: {remote.split("/")[-1]}')
sftp.close()

# 验证
stdin, stdout, stderr = ssh.exec_command('grep -h "const STD\\|const LIMIT" /home/ubuntu/ginseng-project/ginseng-fronted/query.html /home/ubuntu/ginseng-project/ginseng-fronted/statistics.html /home/ubuntu/ginseng-project/ginseng-fronted/admin.html')
print('\n验证标准值:')
print(stdout.read().decode('utf-8','replace'))

ssh.close()
print('\n完成')
