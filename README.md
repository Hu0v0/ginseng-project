# 人参重金属安全检测溯源系统

通化人参重金属检测数据服务平台，含前端展示 + FastAPI 后端 + 数据库，支持检测数据录入、查询、报告下载、数据统计与溯源管理。

## 目录结构

```
ginseng-project/
├── ginseng-backend/          # FastAPI 后端
│   ├── main.py               # 主程序（接口 + 数据库）
│   ├── report_template.py    # PDF 检测报告模板
│   ├── requirements.txt      # Python 依赖
│   └── Dockerfile            # 后端镜像
├── ginseng-fronted/          # 前端静态页面（HTML/CSS/JS）
│   ├── index.html            # 首页
│   ├── detect.html           # 检测服务
│   ├── query.html            # 检测查询 / 报告下载
│   ├── statistics.html       # 数据统计（全量走后端接口）
│   ├── admin.html            # 管理员后台
│   ├── login.html / register.html / my-orders.html / about.html / standard.html
│   ├── css/ js/              # 样式与脚本
│   └── js/api-config.js      # ★ 后端地址配置（部署时改这里）
├── seed_demo.json            # 云端初始化用 98 条演示数据
├── seed_demo.py              # 云端数据灌入脚本（python seed_demo.py --api ...）
├── render.yaml               # Render 免费部署配置
├── docker-compose.yml        # 云服务器一键部署配置
└── .gitignore
```

## 本地运行

1. 启动 MySQL，创建数据库 `ginseng_db`（或直接用已有库）
2. 后端：

```bash
cd ginseng-backend
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

3. 前端静态服务：

```bash
cd ginseng-fronted
python -m http.server 8899
```

4. 浏览器访问 `http://127.0.0.1:8899/index.html`

> 前端已自动判断：本地（127.0.0.1 / localhost）访问时连接 `http://127.0.0.1:8000`，无需配置。

## 后端接口地址配置（关键）

所有前端页面统一读取 `ginseng-fronted/js/api-config.js`：

```js
var CLOUD_API = ''; // ← 云端部署时填后端公网地址，如 'https://xxx.onrender.com'
```

- **本地开发**：留空即可，自动用 `http://127.0.0.1:8000`
- **云端部署**：把 `CLOUD_API` 改成后端公网地址，前端（含 GitHub Pages）即可跨域联动后端

## 部署到云端（三种方式）

### 方式一：GitHub Pages 看界面（免费，最快）

1. 在 GitHub 新建仓库，推送本目录代码
2. 仓库 Settings → Pages → 选择分支 `main` 根目录 → Save
3. 得到网址 `https://你的用户名.github.io/仓库名/index.html`

> 界面可以全球访问；**数据区需要后端支持**才显示（见方式二/三）。

### 方式二：Render 免费后端（前后端真联动，免费额度）

1. 将代码推到 GitHub
2. 打开 [render.com](https://render.com) → New → Blueprint → 选择本仓库
3. Render 按 `render.yaml` 自动创建 PostgreSQL 数据库 + 后端服务
4. 部署完成后复制后端地址，填到前端 `js/api-config.js` 的 `CLOUD_API`，再推一次代码刷新 GitHub Pages

> 注意：免费实例闲置会休眠，首次访问需等几十秒唤醒。

> **云端数据初始化（重要）**：云端是新数据库，本地 98 条检测数据不会自动带上去。
> 部署完成后在项目根目录运行：
> ```bash
> python seed_demo.py --api https://你的后端地址/detection/
> ```
> 即可把 98 条数据灌入云端（已存在的编号自动跳过，可重复运行）。
> 种子数据文件为 `seed_demo.json`。

### 方式三：云服务器 + Docker Compose（正式长期使用）

1. 购买轻量云服务器（腾讯云/阿里云均可），安装 Docker：
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```
2. 上传代码到服务器，进入项目根目录：
   ```bash
   docker compose up -d --build
   ```
3. 安全组放行 80、8000 端口
4. 把 `js/api-config.js` 的 `CLOUD_API` 填为 `http://服务器公网IP:8000`
5. 浏览器访问 `http://服务器公网IP`
6. 云端数据库初始化（新库为空）：
   ```bash
   python seed_demo.py --api http://服务器公网IP:8000/detection/
   ```

> 数据库密码可通过环境变量 `DB_PASSWORD` 修改（`docker compose` 默认 123456，正式使用请改掉）。

## 数据库

- 支持 MySQL（默认）与 PostgreSQL（Render）
- 后端启动时自动建表（`Base.metadata.create_all`）
- 连接参数全部通过环境变量配置：
  `DB_DRIVER / DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME`
