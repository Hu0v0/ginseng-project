# -*- coding: utf-8 -*-
import io, sys, paramiko
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

# 上传本地修改后的 login.html 到服务器
sftp = ssh.open_sftp()
sftp.put(r'D:\ginseng-project\ginseng-fronted\login.html', '/home/ubuntu/ginseng-project/ginseng-fronted/login.html')
sftp.close()
print('login.html 已上传到服务器')

# 确认上传成功
stdin, stdout, stderr = ssh.exec_command('grep -c "测试账号" /home/ubuntu/ginseng-project/ginseng-fronted/login.html')
print('测试账号出现次数:', stdout.read().decode().strip())

ssh.close()
print('完成')
