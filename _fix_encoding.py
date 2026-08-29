# -*- coding: utf-8 -*-
import io, sys, paramiko, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.68.167.116', username='ubuntu', password='Huhuiyan0320', timeout=30)

def run(cmd, t=60):
    print(f'\n$ {cmd[:100]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t)
    print(stdout.read().decode('utf-8','replace'))
    err = stderr.read().decode('utf-8','replace')
    if err: print('[stderr]', err[:200])

# 1. 检查表字符集
run('echo "Huhuiyan0320" | sudo -S docker exec ginseng-mysql mysql -uroot -p123456 ginseng_db -e "SHOW CREATE TABLE detection_records\\G" 2>&1 | head -5')

# 2. 清空旧数据
run('echo "Huhuiyan0320" | sudo -S docker exec ginseng-mysql mysql -uroot -p123456 ginseng_db -e "DELETE FROM detection_records;"')

# 3. 在服务器上生成正确编码的 SQL（用 Python，确保 UTF-8）
python_script = '''
# -*- coding: utf-8 -*-
import random
from datetime import date, timedelta

origins = ["吉林长白山","吉林抚松","吉林集安","黑龙江牡丹江","辽宁桓仁","山东文登","云南文山","贵州施秉"]
names = ["生晒参","红参","白参","西洋参","野山参","林下参","高丽参","糖参"]
ages = ["3年","4年","5年","6年","7年","8年","10年","12年"]
parts = ["根","根茎","叶","花","果"]
inspectors = ["张检测","李质检","王实验","赵分析","陈测试","刘化验","孙检验","周技术"]

rows = []
for i in range(1, 99):
    ok = random.random() < 0.95
    if ok:
        lead=round(random.uniform(0.1,4.5),2); arsenic=round(random.uniform(0.05,1.8),2)
        cadmium=round(random.uniform(0.01,0.25),2); mercury=round(random.uniform(0.005,0.15),2)
    else:
        item=random.choice(["lead","arsenic","cadmium","mercury"])
        lead=round(random.uniform(5.1,12),2) if item=="lead" else round(random.uniform(0.1,4.5),2)
        arsenic=round(random.uniform(2.1,6),2) if item=="arsenic" else round(random.uniform(0.05,1.8),2)
        cadmium=round(random.uniform(0.31,1.2),2) if item=="cadmium" else round(random.uniform(0.01,0.25),2)
        mercury=round(random.uniform(0.21,0.8),2) if item=="mercury" else round(random.uniform(0.005,0.15),2)
    copper=round(random.uniform(1,18),2)
    start=date(2024,1,1); end=date(2026,8,1)
    d=start+timedelta(days=random.randint(0,(end-start).days))
    rows.append(f"('GS{i:05d}','{random.choice(names)}','{random.choice(ages)}','{random.choice(parts)}','{random.choice(origins)}',{lead},{arsenic},{cadmium},{mercury},{copper},'{d}','{random.choice(inspectors)}',NOW())")

sql = "SET NAMES utf8mb4;\\nINSERT INTO detection_records (`sample_id`,`name`,`age`,`part`,`origin`,`lead`,`arsenic`,`cadmium`,`mercury`,`copper`,`detection_date`,`inspector`,`created_at`) VALUES\\n" + ",\\n".join(rows) + ";"
with open('/tmp/seed_utf8.sql','w',encoding='utf-8') as f:
    f.write(sql)
print(f"已生成 {len(rows)} 条，UTF-8 编码")
'''

# 把 Python 脚本写到服务器并执行
sftp = ssh.open_sftp()
with sftp.file('/tmp/gen_utf8.py', 'w') as f:
    f.write(python_script)
sftp.close()
run('python3 /tmp/gen_utf8.py')

# 4. 用 utf8mb4 导入
run('echo "Huhuiyan0320" | sudo -S docker exec -i ginseng-mysql mysql --default-character-set=utf8mb4 -uroot -p123456 ginseng_db < /tmp/seed_utf8.sql')

# 5. 验证中文是否正常
time.sleep(2)
run('curl -s http://127.0.0.1:8000/detection/ | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[\'data\'][0][\'name\'], d[\'data\'][0][\'origin\'], d[\'data\'][0][\'status\'])"')
run('curl -s http://127.0.0.1:8000/statistics/overview')

ssh.close()
print('\n完成')
