from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from io import BytesIO
import os
import qrcode

# 精美版报告模板（report_template.py 与 main.py 同目录）
from report_template import build_report

# -------------------------- 数据库配置 --------------------------
# 通过环境变量读取，便于本地/云端部署切换；未设置时回退本地默认值
# DB_DRIVER 支持 mysql+pymysql（默认）或 postgresql+psycopg2（Render 免费库）
DB_DRIVER = os.getenv("DB_DRIVER", "mysql+pymysql")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "ginseng_db")

if DB_DRIVER.startswith("postgres"):
    SQLALCHEMY_DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    SQLALCHEMY_DATABASE_URL = (
        f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 重金属限量国家标准（单位：mg/kg）
HEAVY_METAL_STANDARD = {
    "lead": 0.05,
    "arsenic": 0.02,
    "cadmium": 0.01,
    "mercury": 0.01,
    "copper": 20.0
}

# -------------------------- 数据表模型 --------------------------
class DetectionRecord(Base):
    __tablename__ = "detection_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sample_id = Column(String(50), unique=True, comment="样本编号")
    name = Column(String(100), comment="人参品种")
    age = Column(String(20), comment="人参年限，如 5年")
    part = Column(String(20), default="根", comment="检测部位：根/茎/叶")
    origin = Column(String(200), comment="产地")
    lead = Column(Float, comment="铅含量")
    arsenic = Column(Float, comment="砷含量")
    cadmium = Column(Float, comment="镉含量")
    mercury = Column(Float, comment="汞含量")
    copper = Column(Float, comment="铜含量")
    detection_date = Column(Date, comment="检测日期")
    inspector = Column(String(50), comment="检测人")
    created_at = Column(DateTime, default=datetime.now, comment="记录创建时间")

# 用户表模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, comment="用户名/登录账号")
    password = Column(String(255), comment="登录密码（明文存储，仅演示用）")
    phone = Column(String(20), comment="手机号码")
    email = Column(String(100), comment="邮箱地址")
    user_type = Column(String(20), default="personal", comment="用户类型：personal个人 / enterprise企业")
    role = Column(String(20), default="user", comment="角色权限：user普通用户 / admin管理员 / inspector检测员")
    created_at = Column(DateTime, default=datetime.now, comment="注册时间")

# 预约订单表模型
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, comment="提交预约的用户ID")
    username = Column(String(50), comment="提交人用户名（冗余，便于管理员查看）")
    service_type = Column(String(50), comment="预约服务类型，如 基础检测套餐")
    contact = Column(String(50), comment="联系人")
    phone = Column(String(20), comment="联系电话")
    sample_count = Column(Integer, default=1, comment="送检样本数量")
    remark = Column(String(500), comment="备注/需求说明")
    status = Column(String(20), default="待处理", comment="状态：待处理/已通过/已驳回")
    admin_reply = Column(String(500), comment="管理员处理意见")
    created_at = Column(DateTime, default=datetime.now, comment="预约提交时间")

Base.metadata.create_all(bind=engine)

# -------------------------- 请求参数模型 --------------------------
class GinsengDetectionCreate(BaseModel):
    sample_id: str
    name: str
    age: Optional[str] = None
    part: Optional[str] = "根"
    origin: str
    lead: float
    arsenic: float
    cadmium: float
    mercury: float
    copper: Optional[float] = None
    detection_date: date
    inspector: str

class GinsengDetectionUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None
    part: Optional[str] = None
    origin: Optional[str] = None
    lead: Optional[float] = None
    arsenic: Optional[float] = None
    cadmium: Optional[float] = None
    mercury: Optional[float] = None
    copper: Optional[float] = None
    detection_date: Optional[date] = None
    inspector: Optional[str] = None

# 用户相关请求模型
class UserRegister(BaseModel):
    username: str
    password: str
    phone: Optional[str] = None
    email: Optional[str] = None
    user_type: Optional[str] = "personal"
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    user_type: Optional[str] = None
    role: Optional[str] = None

# 预约相关请求模型
class OrderCreate(BaseModel):
    user_id: int
    username: str
    service_type: str
    contact: str
    phone: str
    sample_count: Optional[int] = 1
    remark: Optional[str] = None

class OrderHandle(BaseModel):
    status: str            # 已通过 / 已驳回
    admin_reply: Optional[str] = None

# -------------------------- 工具函数 --------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 自动判定是否超标
def check_standard(record: DetectionRecord):
    abnormal = []
    if record.lead is not None and record.lead > HEAVY_METAL_STANDARD["lead"]:
        abnormal.append(f"铅超标(标准{HEAVY_METAL_STANDARD['lead']}mg/kg)")
    if record.arsenic is not None and record.arsenic > HEAVY_METAL_STANDARD["arsenic"]:
        abnormal.append(f"砷超标(标准{HEAVY_METAL_STANDARD['arsenic']}mg/kg)")
    if record.cadmium is not None and record.cadmium > HEAVY_METAL_STANDARD["cadmium"]:
        abnormal.append(f"镉超标(标准{HEAVY_METAL_STANDARD['cadmium']}mg/kg)")
    if record.mercury is not None and record.mercury > HEAVY_METAL_STANDARD["mercury"]:
        abnormal.append(f"汞超标(标准{HEAVY_METAL_STANDARD['mercury']}mg/kg)")
    if record.copper is not None and record.copper > HEAVY_METAL_STANDARD["copper"]:
        abnormal.append(f"铜超标(标准{HEAVY_METAL_STANDARD['copper']}mg/kg)")
    return {
        "status": "不合格" if abnormal else "合格",
        "abnormal_items": abnormal
    }

# 拼接返回数据
def record_with_result(record: DetectionRecord):
    base = {
        "id": record.id,
        "sample_id": record.sample_id,
        "name": record.name,
        "age": record.age,
        "part": record.part,
        "origin": record.origin,
        "lead": record.lead,
        "arsenic": record.arsenic,
        "cadmium": record.cadmium,
        "mercury": record.mercury,
        "copper": record.copper,
        "detection_date": record.detection_date,
        "inspector": record.inspector,
        "created_at": record.created_at
    }
    base.update(check_standard(record))
    return base

# 拼接用户返回数据（不含密码）
def user_to_dict(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "phone": user.phone,
        "email": user.email,
        "user_type": user.user_type,
        "role": user.role,
        "created_at": user.created_at
    }

# 拼接预约订单返回数据
def order_to_dict(order: Order):
    return {
        "id": order.id,
        "user_id": order.user_id,
        "username": order.username,
        "service_type": order.service_type,
        "contact": order.contact,
        "phone": order.phone,
        "sample_count": order.sample_count,
        "remark": order.remark,
        "status": order.status,
        "admin_reply": order.admin_reply,
        "created_at": order.created_at
    }

# -------------------------- 服务初始化 --------------------------
app = FastAPI(
    title="人参重金属检测溯源系统",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------- 基础CRUD接口 --------------------------
@app.get("/", summary="系统测试接口")
def hello():
    return {"code": 200, "msg": "后端服务启动成功", "data": "人参检测系统"}

@app.post("/detection/", summary="录入人参检测数据")
def add_detection(item: GinsengDetectionCreate):
    db = next(get_db())
    exist = db.query(DetectionRecord).filter(DetectionRecord.sample_id == item.sample_id).first()
    if exist:
        return {"code": 400, "msg": "该样本编号已存在，请勿重复录入"}
    db_record = DetectionRecord(**item.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return {"code": 200, "msg": "数据录入成功", "data": db_record.id}

@app.get("/detection/", summary="查询所有检测记录")
def get_all_detection():
    db = next(get_db())
    records = db.query(DetectionRecord).order_by(DetectionRecord.id.desc()).all()
    result = [record_with_result(r) for r in records]
    return {"code": 200, "msg": "查询成功", "data": result}

@app.get("/detection/id/{record_id}", summary="根据ID查询检测详情")
def get_detection_by_id(record_id: int):
    db = next(get_db())
    record = db.query(DetectionRecord).filter(DetectionRecord.id == record_id).first()
    if not record:
        return {"code": 404, "msg": "未找到该记录"}
    return {"code": 200, "msg": "查询成功", "data": record_with_result(record)}

@app.get("/detection/sample/{sample_id}", summary="根据样本编号查询详情")
def get_detection_by_sample(sample_id: str):
    db = next(get_db())
    record = db.query(DetectionRecord).filter(DetectionRecord.sample_id == sample_id).first()
    if not record:
        return {"code": 404, "msg": "未找到该样本数据"}
    return {"code": 200, "msg": "查询成功", "data": record_with_result(record)}

@app.put("/detection/{record_id}", summary="修改检测数据")
def update_detection(record_id: int, item: GinsengDetectionUpdate):
    db = next(get_db())
    record = db.query(DetectionRecord).filter(DetectionRecord.id == record_id).first()
    if not record:
        return {"code": 404, "msg": "未找到该记录"}
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    db.commit()
    return {"code": 200, "msg": "修改成功"}

@app.delete("/detection/{record_id}", summary="删除检测数据")
def delete_detection(record_id: int):
    db = next(get_db())
    record = db.query(DetectionRecord).filter(DetectionRecord.id == record_id).first()
    if not record:
        return {"code": 404, "msg": "未找到该记录"}
    db.delete(record)
    db.commit()
    return {"code": 200, "msg": "删除成功"}

@app.get("/statistics/overview", summary="获取数据统计概览")
def get_statistics():
    db = next(get_db())
    total = db.query(DetectionRecord).count()
    records = db.query(DetectionRecord).all()
    qualified = sum(1 for r in records if check_standard(r)["status"] == "合格")
    unqualified = total - qualified
    origin_list = list(set([r.origin for r in records]))
    return {
        "code": 200,
        "msg": "统计成功",
        "data": {
            "total_count": total,
            "qualified_count": qualified,
            "unqualified_count": unqualified,
            "qualified_rate": round(qualified/total*100, 2) if total > 0 else 0,
            "origin_count": len(origin_list)
        }
    }

@app.get("/statistics/monthly", summary="按月统计检测量（合格/超标）")
def get_monthly_statistics():
    db = next(get_db())
    records = db.query(DetectionRecord).all()
    # 按 年-月 聚合
    month_map = {}
    for r in records:
        if not r.detection_date:
            continue
        key = r.detection_date.strftime("%Y-%m")
        if key not in month_map:
            month_map[key] = {"month": key, "qualified": 0, "unqualified": 0}
        if check_standard(r)["status"] == "合格":
            month_map[key]["qualified"] += 1
        else:
            month_map[key]["unqualified"] += 1
    # 按月份升序排列
    result = [month_map[k] for k in sorted(month_map.keys())]
    return {"code": 200, "msg": "统计成功", "data": result}

@app.get("/statistics/elements", summary="各重金属元素超标分布统计")
def get_element_statistics():
    db = next(get_db())
    records = db.query(DetectionRecord).all()
    total = len(records)
    # 元素定义：字段名、符号、中文名、标准限值
    element_defs = [
        {"field": "lead", "sym": "Pb", "name": "铅", "std": HEAVY_METAL_STANDARD["lead"]},
        {"field": "cadmium", "sym": "Cd", "name": "镉", "std": HEAVY_METAL_STANDARD["cadmium"]},
        {"field": "arsenic", "sym": "As", "name": "砷", "std": HEAVY_METAL_STANDARD["arsenic"]},
        {"field": "mercury", "sym": "Hg", "name": "汞", "std": HEAVY_METAL_STANDARD["mercury"]},
        {"field": "copper", "sym": "Cu", "name": "铜", "std": HEAVY_METAL_STANDARD["copper"]},
    ]
    result = []
    for e in element_defs:
        exceed = 0
        for r in records:
            value = getattr(r, e["field"])
            if value is not None and e["std"] is not None and value > e["std"]:
                exceed += 1
        result.append({
            "sym": e["sym"],
            "name": e["name"],
            "std": e["std"],
            "exceed_count": exceed,
            "exceed_rate": round(exceed / total * 100, 2) if total > 0 else 0
        })
    return {"code": 200, "msg": "统计成功", "data": {"total": total, "elements": result}}

# -------------------------- 用户管理接口 --------------------------
@app.post("/user/register", summary="用户注册")
def register_user(item: UserRegister):
    db = next(get_db())
    exist = db.query(User).filter(User.username == item.username).first()
    if exist:
        return {"code": 400, "msg": "该用户名已被注册，请更换"}
    if item.phone:
        phone_exist = db.query(User).filter(User.phone == item.phone).first()
        if phone_exist:
            return {"code": 400, "msg": "该手机号已被注册"}
    db_user = User(**item.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"code": 200, "msg": "注册成功", "data": user_to_dict(db_user)}

@app.post("/user/login", summary="用户登录")
def login_user(item: UserLogin):
    db = next(get_db())
    user = db.query(User).filter(User.username == item.username).first()
    if not user:
        return {"code": 404, "msg": "用户不存在"}
    if user.password != item.password:
        return {"code": 401, "msg": "密码错误"}
    return {"code": 200, "msg": "登录成功", "data": user_to_dict(user)}

@app.get("/user/", summary="查询所有用户")
def get_all_users():
    db = next(get_db())
    users = db.query(User).order_by(User.id.desc()).all()
    return {"code": 200, "msg": "查询成功", "data": [user_to_dict(u) for u in users]}

@app.get("/user/{user_id}", summary="根据ID查询用户详情")
def get_user_by_id(user_id: int):
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"code": 404, "msg": "未找到该用户"}
    return {"code": 200, "msg": "查询成功", "data": user_to_dict(user)}

@app.put("/user/{user_id}", summary="修改用户信息")
def update_user(user_id: int, item: UserUpdate):
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"code": 404, "msg": "未找到该用户"}
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    return {"code": 200, "msg": "修改成功", "data": user_to_dict(user)}

@app.delete("/user/{user_id}", summary="删除用户")
def delete_user(user_id: int):
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"code": 404, "msg": "未找到该用户"}
    db.delete(user)
    db.commit()
    return {"code": 200, "msg": "删除成功"}

# -------------------------- 预约订单接口 --------------------------
@app.post("/order/", summary="用户提交预约")
def create_order(item: OrderCreate):
    db = next(get_db())
    order = Order(**item.dict())
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"code": 200, "msg": "预约提交成功，请等待管理员审核", "data": order_to_dict(order)}

@app.get("/order/", summary="查询所有预约（管理员）")
def get_all_orders(status: Optional[str] = None):
    db = next(get_db())
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    orders = query.order_by(Order.created_at.desc()).all()
    return {"code": 200, "msg": "查询成功", "data": [order_to_dict(o) for o in orders]}

@app.get("/order/my/{user_id}", summary="查询某用户的预约")
def get_my_orders(user_id: int):
    db = next(get_db())
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
    return {"code": 200, "msg": "查询成功", "data": [order_to_dict(o) for o in orders]}

@app.put("/order/handle/{order_id}", summary="管理员处理预约（通过/驳回）")
def handle_order(order_id: int, item: OrderHandle):
    db = next(get_db())
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"code": 404, "msg": "未找到该预约"}
    order.status = item.status
    order.admin_reply = item.admin_reply
    db.commit()
    return {"code": 200, "msg": "处理成功", "data": order_to_dict(order)}

@app.delete("/order/{order_id}", summary="删除预约")
def delete_order(order_id: int):
    db = next(get_db())
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"code": 404, "msg": "未找到该预约"}
    db.delete(order)
    db.commit()
    return {"code": 200, "msg": "删除成功"}

# -------------------------- 亮点功能1：溯源二维码生成 --------------------------
@app.get("/trace/qrcode/{sample_id}", summary="生成溯源二维码")
def generate_qrcode(sample_id: str):
    db = next(get_db())
    record = db.query(DetectionRecord).filter(DetectionRecord.sample_id == sample_id).first()
    if not record:
        return {"code": 404, "msg": "未找到该样本，无法生成二维码"}
    
    # 溯源链接，后续做前端页面后可替换为前端溯源页地址
    trace_url = f"http://127.0.0.1:8000/detection/sample/{sample_id}"
    
    # 生成二维码图片
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(trace_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 转成图片流直接返回，不保存本地文件
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

# -------------------------- 亮点功能2：PDF检测报告导出（精美版模板） --------------------------
@app.get("/detection/report/{sample_id}", summary="导出检测报告PDF")
def export_report(sample_id: str):
    db = next(get_db())
    record = db.query(DetectionRecord).filter(DetectionRecord.sample_id == sample_id).first()
    if not record:
        return {"code": 404, "msg": "未找到该样本，无法生成报告"}

    result = check_standard(record)
    conclusion = "合格" if result["status"] == "合格" else "部分超标"

    # 组装模板数据
    elements = [
        ("铅", "Pb", record.lead, HEAVY_METAL_STANDARD["lead"]),
        ("砷", "As", record.arsenic, HEAVY_METAL_STANDARD["arsenic"]),
        ("镉", "Cd", record.cadmium, HEAVY_METAL_STANDARD["cadmium"]),
        ("汞", "Hg", record.mercury, HEAVY_METAL_STANDARD["mercury"]),
        ("铜", "Cu", record.copper, HEAVY_METAL_STANDARD["copper"]),
    ]
    report_id = f"DA{record.detection_date:%Y%m%d}{record.id:05d}" if record.detection_date else f"DA{record.sample_id}"

    data = {
        "report_id": report_id,
        "sample_id": record.sample_id,
        "name": record.name,
        "age": record.age,
        "origin": record.origin,
        "part": record.part,
        "method": "微波消解-ICP-MS",
        "date": str(record.detection_date) if record.detection_date else "",
        "org": "通化师范学院化学实训中心",
        "elements": elements,
        "conclusion": conclusion,
    }

    buf = build_report(data)

    # 设置下载文件名（Content-Disposition 头仅支持 latin-1，需用 RFC 5987 filename* 才允许中文）
    from urllib.parse import quote as _urlquote
    safe_name = _urlquote(f"检测报告_{sample_id}.pdf", safe="")
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{safe_name}"
    }
    return StreamingResponse(buf, media_type="application/pdf", headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# ---- 兼容性路由别名（前端曾用过这些路径，保留以保证向后兼容）----
@app.get("/detection/pdf/{sample_id}")
def _pdf_alias(sample_id: str): return export_report(sample_id)

@app.get("/detection/qrcode/{sample_id}")
def _qrcode_alias(sample_id: str): return generate_qrcode(sample_id)