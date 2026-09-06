# 🌿 参安 · 人参重金属安全检测溯源系统

> 通化师范学院化学实训中心 · 人参重金属检测数据服务平台
> 集 **检测数据录入、查询溯源、PDF 报告生成、数据统计、用户与预约管理** 于一体的全栈 Web 系统。

在线体验：<https://hu0v0.github.io/ginseng-project/> ｜ 云端部署：<http://81.68.167.116/>（截止至 2026.9.29）

---

## ✨ 功能特性

- 📋 **检测数据管理**：录入 / 编辑 / 删除人参重金属检测记录，支持按样本编号、产区、状态筛选
- 🔍 **检测查询**：按样本编号精准查询，展示铅、砷、镉、汞、铜五项重金属实测值与国标限量对比
- 📄 **PDF 检测报告**：一键导出精美版 PDF 报告（《中国药典》2020 版限量标准，含合格/超标结论）
- 📊 **数据统计**：总览卡片、月度趋势图、元素超标分布、产区合格率、园参/林下参对比、年限与部位分析
- 🔗 **溯源二维码**：每份样本一键生成溯源二维码，扫码直达检测报告详情
- 👥 **用户体系**：注册 / 登录 / 角色权限（管理员、检测员、普通用户），管理员后台管理用户
- 📅 **预约服务**：用户提交检测预约，管理员审核通过/驳回
- 🏭 **标准法规**：内置人参重金属限量标准与相关法规文档

## 🛠️ 技术栈

| 层 | 技术 |
|---|---|
| 前端 | HTML5 · CSS3 · 原生 JavaScript · ECharts 图表 |
| 后端 | Python 3.11 · FastAPI · SQLAlchemy · ReportLab（PDF）· qrcode |
| 数据库 | MySQL 8.0（默认） / PostgreSQL（兼容） |
| 部署 | Docker Compose（云服务器一键部署） · Nginx · GitHub Pages |

## 📁 目录结构

```
ginseng-project/
├── ginseng-backend/            # FastAPI 后端
│   ├── main.py                 # 主程序：接口路由 + 数据库模型 + 业务逻辑
│   ├── report_template.py      # PDF 检测报告精美模板（ReportLab）
│   ├── requirements.txt        # Python 依赖
│   └── Dockerfile              # 后端容器镜像
├── ginseng-fronted/            # 前端静态页面
│   ├── index.html              # 首页
│   ├── detect.html             # 检测服务
│   ├── query.html              # 检测查询 / 报告下载 / 溯源二维码
│   ├── statistics.html         # 数据统计（全部走后端接口）
│   ├── admin.html              # 管理员后台（样本 / 用户 / 预约管理）
│   ├── login.html              # 登录（含测试账号提示）
│   ├── register.html           # 注册
│   ├── my-orders.html          # 我的预约
│   ├── about.html              # 关于我们
│   ├── standard.html           # 标准法规
│   ├── css/                    # 统一样式（common.css）
│   └── js/                     # 脚本 + ★api-config.js 后端地址配置
├── seed_demo.json              # 98 条云端初始化演示数据
├── seed_demo.py                # 数据灌入脚本：python seed_demo.py --api <后端地址>/detection/
├── docker-compose.yml          # 云服务器一键部署（MySQL + 后端 + 前端）
└── README.md
```

## 🚀 快速开始（本地开发）

### 1. 启动数据库

本地安装 MySQL 8.0，创建数据库：

```sql
CREATE DATABASE ginseng_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 启动后端

```bash
cd ginseng-backend
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

后端启动时会自动建表，访问 <http://127.0.0.1:8000/docs> 可查看 Swagger 接口文档。

### 3. 启动前端

```bash
cd ginseng-fronted
python -m http.server 8899
```

浏览器打开 <http://127.0.0.1:8899/index.html>

> 前端自动判断：本地（127.0.0.1 / localhost）访问时连接 `http://127.0.0.1:8000`，无需额外配置。

### 4.（可选）灌入演示数据

```bash
python seed_demo.py --api http://127.0.0.1:8000/detection/
```

## 🔌 后端接口概览

基础路径：`http://<host>:8000`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 健康检查 |
| POST | `/detection/` | 录入检测数据 |
| GET | `/detection/` | 查询全部检测记录 |
| GET | `/detection/id/{id}` | 按 ID 查详情 |
| GET | `/detection/sample/{sample_id}` | 按样本编号查详情 |
| PUT | `/detection/{id}` | 修改检测数据 |
| DELETE | `/detection/{id}` | 删除检测数据 |
| GET | `/detection/report/{sample_id}` | **导出 PDF 检测报告** |
| GET | `/trace/qrcode/{sample_id}` | 生成溯源二维码（PNG） |
| GET | `/statistics/overview` | 总览统计（总数/合格率/产区数） |
| GET | `/statistics/monthly` | 月度检测量趋势 |
| GET | `/statistics/elements` | 各元素超标分布 |
| POST | `/user/register` | 用户注册 |
| POST | `/user/login` | 用户登录 |
| GET | `/user/` | 用户列表（管理员） |
| PUT | `/user/{id}` | 修改用户 |
| DELETE | `/user/{id}` | 删除用户 |
| POST | `/order/` | 提交检测预约 |
| GET | `/order/my/{user_id}` | 我的预约 |
| PUT | `/order/handle/{id}` | 管理员处理预约 |
| DELETE | `/order/{id}` | 删除预约 |

## ⚖️ 重金属限量标准

依据《中国药典》2020 年版（单位：mg/kg），前后端统一：

| 元素 | 限量 |
|---|---|
| 铅 Pb | ≤ 5.0 |
| 砷 As | ≤ 2.0 |
| 镉 Cd | ≤ 0.3 |
| 汞 Hg | ≤ 0.2 |
| 铜 Cu | ≤ 20.0 |

## 🗄️ 数据库说明

- 表结构：`detection_records`（检测记录）、`users`（用户）、`orders`（预约）
- 后端启动自动建表，连接参数通过环境变量配置：
  `DB_DRIVER / DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME`
- 默认（Docker Compose）：MySQL 8.0，root / 123456，库名 `ginseng_db`

## 📄 License

本项目为通化师范学院化学实训中心教学科研项目，仅用于学习与交流。
