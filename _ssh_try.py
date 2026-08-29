# -*- coding: utf-8 -*-
import io, sys, paramiko
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = '81.68.167.116'
PWD = 'Huhuiyan0320'

for user in ['root', 'ubuntu']:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=user, password=PWD, timeout=20)
        print(f'✅ {user} 登录成功！')
        stdin, stdout, stderr = ssh.exec_command('whoami && cat /etc/os-release | head -3')
        print(stdout.read().decode())
        ssh.close()
        break
    except paramiko.AuthenticationException:
        print(f'❌ {user} 认证失败（密码错误）')
    except Exception as e:
        print(f'❌ {user} 错误: {e}')
    finally:
        try: ssh.close()
        except: pass
