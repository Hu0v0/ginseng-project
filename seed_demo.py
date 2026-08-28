# -*- coding: utf-8 -*-
"""
云端数据初始化脚本
==================
把本地的 98 条检测数据灌入云端（或任意）后端数据库。

用法（在项目根目录执行）：
    本地后端：  python seed_demo.py
    云端后端：  python seed_demo.py --api https://你的后端地址/detection/

原理：逐条调用后端 POST /detection/ 接口录入，无需直接连接数据库。
重复运行安全：已存在的样本编号会自动跳过。
"""
import sys
import json
import time
import argparse
import urllib.request

HERE = __import__('os').path.dirname(__file__)
SEED_FILE = __import__('os').path.join(HERE, 'seed_demo.json')


def post(api, payload, retries=3):
    last = None
    for _ in range(retries):
        req = urllib.request.Request(
            api,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            try:
                return json.loads(e.read().decode('utf-8'))
            except Exception:
                return {'code': e.code, 'msg': str(e)}
        except Exception as e:
            last = e
            time.sleep(1)
    return {'code': -1, 'msg': f'{last}'}


def main():
    ap = argparse.ArgumentParser(description='人参检测数据云端初始化')
    ap.add_argument('--api', default='http://127.0.0.1:8000/detection/',
                    help='后端检测录入接口地址，云端示例：https://xxx.onrender.com/detection/')
    args = ap.parse_args()

    with open(SEED_FILE, encoding='utf-8') as f:
        rows = json.load(f)
    print(f'种子文件共 {len(rows)} 条数据，目标接口: {args.api}')

    ok, skip, fail = 0, 0, []
    for i, r in enumerate(rows, 1):
        rsp = post(args.api, r)
        if rsp.get('code') == 200:
            ok += 1
        elif rsp.get('code') == 400:  # 样本编号已存在
            skip += 1
        else:
            fail.append((r['sample_id'], rsp.get('msg')))
        if i % 10 == 0:
            print(f'  进度 {i}/{len(rows)} ...')
            time.sleep(0.3)

    print(f'\n完成：成功 {ok} 条，跳过(已存在) {skip} 条，失败 {len(fail)} 条')
    if fail:
        print('失败明细（前 5 条）：')
        for sid, msg in fail[:5]:
            print(f'  {sid}: {msg}')


if __name__ == '__main__':
    main()
