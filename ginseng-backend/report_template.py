# -*- coding: utf-8 -*-
"""
人参重金属检测报告 —— 精美版 PDF 生成模块（供后端 export_report 调用）
A4 单页正式检测报告，深绿+金色系。
特色：canvas 页眉徽章 / 金色装饰线 / 结论卡 / 红色印章 / 淡色水印 / 圆角表格
"""
import os
import math
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Flowable)

# ---------- 1. 中文字体 ----------
FONT_DIR = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("SimHei", os.path.join(FONT_DIR, "simhei.ttf")))
pdfmetrics.registerFont(TTFont("SimSun", os.path.join(FONT_DIR, "simsun.ttc"), subfontIndex=0))
pdfmetrics.registerFont(TTFont("SimKai", os.path.join(FONT_DIR, "simkai.ttf")))
pdfmetrics.registerFontFamily("SimSun", normal="SimSun", bold="SimHei",
                              italic="SimSun", boldItalic="SimHei")

# ---------- 2. 配色 ----------
C_PRIMARY   = colors.HexColor("#1F5E3A")   # 主色 深绿
C_PRIMARY_D = colors.HexColor("#173F2B")   # 更深绿（标题）
C_GOLD      = colors.HexColor("#C9A063")   # 金
C_GOLD_L    = colors.HexColor("#E3CDA4")   # 浅金
C_CREAM     = colors.HexColor("#F8F5EF")   # 米色底
C_GREEN_L   = colors.HexColor("#EAF4EC")   # 浅绿底
C_GREEN     = colors.HexColor("#2E7D32")   # 合格绿
C_RED       = colors.HexColor("#C62828")   # 超标红
C_RED_L     = colors.HexColor("#FBE9E9")   # 浅红底
C_LINE      = colors.HexColor("#DCE3DC")   # 细线
C_TEXT      = colors.HexColor("#2B2B2B")
C_MUTED     = colors.HexColor("#77817A")
C_SEAL      = colors.HexColor("#C0272D")   # 印章红

# 报告检测机构（印章文字、机构名共用）
REPORT_ORG = "通化师范学院化学实训中心"
REPORT_ORG_SHORT = "参安"
DEFAULT_METHOD = "微波消解-ICP-MS"

# ---------- 3. 样式 ----------
S_TITLE = ParagraphStyle("title", fontName="SimHei", fontSize=22, leading=28,
                         alignment=TA_CENTER, textColor=C_PRIMARY_D)
S_SUB   = ParagraphStyle("sub", fontName="SimSun", fontSize=9.5, leading=14,
                         alignment=TA_CENTER, textColor=C_GOLD, spaceBefore=1)
S_ORG   = ParagraphStyle("org", fontName="SimKai", fontSize=13.5, leading=18,
                         alignment=TA_CENTER, textColor=C_PRIMARY, spaceBefore=2)
S_SECT  = ParagraphStyle("sect", fontName="SimHei", fontSize=12, leading=16,
                         textColor=C_PRIMARY_D)
S_LABEL = ParagraphStyle("label", fontName="SimSun", fontSize=9.5, leading=14,
                         textColor=C_MUTED)
S_VALUE = ParagraphStyle("value", fontName="SimHei", fontSize=10, leading=14,
                         textColor=C_TEXT)
S_CELL  = ParagraphStyle("cell", fontName="SimSun", fontSize=10, leading=14,
                         alignment=TA_CENTER, textColor=C_TEXT)
S_CELLH = ParagraphStyle("cellh", fontName="SimHei", fontSize=10.5, leading=14,
                         alignment=TA_CENTER, textColor=colors.white)
S_BADGE_OK  = ParagraphStyle("ok", fontName="SimHei", fontSize=9, leading=12,
                             alignment=TA_CENTER, textColor=C_GREEN,
                             backColor=C_GREEN_L, borderColor=C_GREEN,
                             borderWidth=0.6, borderRadius=7,
                             leftPadding=7, rightPadding=7, topPadding=1.5, bottomPadding=1.5)
S_BADGE_BAD = ParagraphStyle("bad", fontName="SimHei", fontSize=9, leading=12,
                             alignment=TA_CENTER, textColor=C_RED,
                             backColor=C_RED_L, borderColor=C_RED,
                             borderWidth=0.6, borderRadius=7,
                             leftPadding=7, rightPadding=7, topPadding=1.5, bottomPadding=1.5)
S_BODY  = ParagraphStyle("body", fontName="SimSun", fontSize=10, leading=16, textColor=C_TEXT)
S_REMARK= ParagraphStyle("remark", fontName="SimSun", fontSize=9, leading=14,
                         textColor=C_MUTED)
S_SIGN  = ParagraphStyle("sign", fontName="SimKai", fontSize=11, leading=16, textColor=C_TEXT)
S_SIGN_L= ParagraphStyle("signl", fontName="SimSun", fontSize=10, leading=14, textColor=C_MUTED)

# ---------- 4. 自定义装饰 Flowable ----------

def draw_h_gradient(c, x, y, w, h, stops, bands=80):
    """用多条窄色带模拟水平线性渐变（规避 reportlab linearGradient 的渲染兼容问题）"""
    for i in range(bands):
        t = i / (bands - 1) if bands > 1 else 0
        col = stops[-1][1]
        for j in range(len(stops) - 1):
            p0, c0 = stops[j]
            p1, c1 = stops[j + 1]
            if p0 <= t <= p1:
                tt = (t - p0) / (p1 - p0) if p1 > p0 else 0
                col = colors.Color(
                    c0.red + (c1.red - c0.red) * tt,
                    c0.green + (c1.green - c0.green) * tt,
                    c0.blue + (c1.blue - c0.blue) * tt)
                break
        c.setFillColor(col)
        c.rect(x + i * (w / bands), y, w / bands + 0.6, h, stroke=0, fill=1)


class GoldLine(Flowable):
    """金色水平渐变装饰线"""
    def __init__(self, width, height=2.2):
        Flowable.__init__(self)
        self.w = width; self.h = height
    def wrap(self, aw, ah):
        return self.w, self.h
    def draw(self):
        c = self.canv
        c.saveState()
        draw_h_gradient(c, 0, 0, self.w, self.h,
                        [(0.0, C_GOLD_L), (0.5, C_GOLD), (1.0, C_GOLD_L)])
        c.restoreState()


def make_conclusion_card(title, title_color, text, bg, bar, width=16.5*cm):
    """结论卡片：浅色底 + 左侧色条 + 标题 + 正文（用标准 Table 布局，避免文字重叠）"""
    st_t = ParagraphStyle("cardt", fontName="SimHei", fontSize=12.5,
                          leading=17, textColor=title_color, spaceAfter=5)
    st_b = ParagraphStyle("cardb", fontName="SimSun", fontSize=10,
                          leading=16, textColor=C_TEXT)
    inner = Table(
        [[Paragraph(title, st_t)],
         [Paragraph(text, st_b)]],
        colWidths=[width - 2.0*cm])
    inner.setStyle(TableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    card = Table([[inner]], colWidths=[width])
    card.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("LINEBEFORE", (0,0), (0,-1), 4, bar),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("LEFTPADDING", (0,0), (-1,-1), 16),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
    ]))
    return card


class StampFlowable(Flowable):
    """红色圆形检测专用章（示意）"""
    def __init__(self, size=3.0*cm):
        Flowable.__init__(self)
        self.size = size
    def wrap(self, aw, ah):
        return self.size, self.size
    def draw(self):
        c = self.canv
        c.saveState()
        r = self.size / 2.0
        c.setFillColor(C_SEAL); c.setStrokeColor(C_SEAL)
        # 双圆环
        c.setLineWidth(1.5)
        c.circle(r, r, r - 0.6, stroke=1, fill=0)
        c.setLineWidth(0.7)
        c.circle(r, r, r - 4.5, stroke=1, fill=0)
        # 环形文字（顶部正立、底部倒立，公章样式）
        c.setFont("SimSun", 8)
        texts = REPORT_ORG
        rr = r - 8.0
        step = math.pi / (len(texts) - 1)
        c.saveState()
        c.translate(r, r)
        for i, ch in enumerate(texts):
            theta = math.pi - i * step  # 180°(左) -> 0°(右) 沿顶部弧
            x = rr * math.cos(theta)
            y = rr * math.sin(theta)
            c.saveState()
            c.translate(x, y)
            c.rotate(math.degrees(theta) - 90)
            c.drawCentredString(0, 0, ch)
            c.restoreState()
        c.restoreState()
        # 中心五角星 + 文字
        c.setFont("SimHei", 9)
        c.drawCentredString(r, r + 3.5, "检测专用")
        c.setFont("SimHei", 9)
        c.drawCentredString(r, r - 5.5, "章")
        c.restoreState()


# ---------- 5. 主构建函数 ----------
def build_report(data):
    """
    根据检测记录数据生成报告 PDF，返回 BytesIO。
    data 字段：
      report_id  报告编号（页眉右上）
      sample_id  样本编号
      name       人参品种
      age        生长年限
      origin     产地
      part       检测部位
      method     检测方法
      date       检测日期（str）
      org        检测机构名称（默认 REPORT_ORG）
      elements   列表，每项 (名称, 符号, 实测值或None, 国标限值)
      conclusion "合格" 或 "部分超标"
    """
    org = data.get("org") or REPORT_ORG
    report_id = data.get("report_id") or data.get("sample_id", "")
    det_date = data.get("date", "")
    method = data.get("method") or DEFAULT_METHOD
    conclusion = data.get("conclusion", "合格")

    # 标题区（两侧金线）
    story = []
    story.append(Spacer(1, 1.12*cm))
    title_line_w = 3.2*cm
    title_tbl = Table(
        [[GoldLine(title_line_w), "", GoldLine(title_line_w)]],
        colWidths=[title_line_w, 7.4*cm, title_line_w])
    title_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    title_tbl._cellvalues[0][1] = Paragraph("人参重金属检测报告", S_TITLE)
    story.append(title_tbl)
    story.append(Paragraph("GINSENG HEAVY METAL DETECTION REPORT", S_SUB))
    story.append(Spacer(1, 0.28*cm))
    story.append(Paragraph(org, S_ORG))
    story.append(Spacer(1, 0.34*cm))

    def section(title):
        """章节标题（纯文字，不带装饰方块）"""
        return Paragraph(title, S_SECT)

    # --- 一、样本基本信息 ---
    story.append(section("一、样本基本信息"))
    story.append(Spacer(1, 0.18*cm))
    basic_tbl = Table(
        [[Paragraph("样本编号", S_LABEL), Paragraph(str(data.get("sample_id", "—")), S_VALUE),
          Paragraph("人参品种", S_LABEL), Paragraph(str(data.get("name", "—")), S_VALUE)],
         [Paragraph("生长年限", S_LABEL), Paragraph(str(data.get("age", "—")), S_VALUE),
          Paragraph("产地", S_LABEL),     Paragraph(str(data.get("origin", "—")), S_VALUE)],
         [Paragraph("检测部位", S_LABEL), Paragraph(str(data.get("part", "根")), S_VALUE),
          Paragraph("检测方法", S_LABEL), Paragraph(method, S_VALUE)],
         [Paragraph("检测日期", S_LABEL), Paragraph(det_date, S_VALUE), "", ""]],
        colWidths=[2.4*cm, 4.1*cm, 2.4*cm, 4.1*cm])
    basic_tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.7, C_LINE),
        ("BACKGROUND", (0,0), (0,-1), C_CREAM),
        ("BACKGROUND", (2,0), (2,-1), C_CREAM),
        ("SPAN", (2,3), (3,3)),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(basic_tbl)
    story.append(Spacer(1, 0.34*cm))

    # --- 二、重金属检测结果 ---
    story.append(section("二、重金属检测结果"))
    story.append(Spacer(1, 0.18*cm))
    header = ["检测项目", "元素符号", "实测值 (mg/kg)", "国家标准限值 (mg/kg)", "判定结果"]
    rows = [[Paragraph(h, S_CELLH) for h in header]]
    for item, sym, val, limit in data.get("elements", []):
        if val is None:
            rows.append([
                Paragraph(f"{item}（{sym}）", S_CELL),
                Paragraph(sym, S_CELL),
                Paragraph("—", S_CELL),
                Paragraph(f"{limit}", S_CELL),
                Paragraph("未检", S_BADGE_BAD),
            ])
            continue
        ok = val <= limit
        rows.append([
            Paragraph(f"{item}（{sym}）", S_CELL),
            Paragraph(sym, S_CELL),
            Paragraph(f"{val}", S_CELL),
            Paragraph(f"{limit}", S_CELL),
            Paragraph("合格" if ok else "超标", S_BADGE_OK if ok else S_BADGE_BAD),
        ])
    detect_tbl = Table(rows, colWidths=[3.4*cm, 2.4*cm, 3.2*cm, 4.2*cm, 3.0*cm])
    detect_tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.7, C_LINE),
        ("BACKGROUND", (0,0), (-1,0), C_PRIMARY),
        ("LINEBELOW", (0,0), (-1,0), 1.2, C_GOLD),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, C_CREAM]),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(detect_tbl)
    story.append(Spacer(1, 0.34*cm))

    # --- 检测结论（卡片）---
    if conclusion == "合格":
        concl_title = "检测结论：合格"
        concl_color = C_GREEN
        concl_text = ("本次检测的人参样品各项重金属含量均符合《中国药典》2020年版限量标准。"
                      "建议在采收后及时加工储藏，保持良好的种植环境，持续关注土壤质量变化。"
                      "本报告可作为交易议价的参考依据。")
        card = make_conclusion_card(concl_title, concl_color, concl_text,
                                    colors.HexColor("#EAF4EC"), C_GREEN)
    else:
        concl_title = "检测结论：部分超标"
        concl_color = C_RED
        concl_text = ("本次检测的人参样品中存在重金属超标情况。建议排查土壤污染源并采取土壤改良措施，"
                      "暂停该批次上市销售，并尽快联系我们获取专业处理方案。")
        card = make_conclusion_card(concl_title, concl_color, concl_text,
                                    colors.HexColor("#FBE9E9"), C_RED)
    story.append(card)
    story.append(Spacer(1, 0.34*cm))

    # --- 三、检测依据与说明 ---
    story.append(section("三、检测依据与说明"))
    story.append(Spacer(1, 0.14*cm))
    story.append(Paragraph("1. 检测依据：《中华人民共和国药典》2020年版 及 GB 2762-2022《食品安全国家标准 食品中污染物限量》。", S_BODY))
    story.append(Spacer(1, 0.06*cm))
    story.append(Paragraph("2. 本报告由系统依据检测数据自动生成，数据真实可溯源；如有异议，请于报告签发之日起 15 个工作日内提出复核申请。", S_REMARK))
    story.append(Spacer(1, 0.3*cm))

    # --- 签发区（盖章 + 印章 + 日期）---
    sign_tbl = Table(
        [[Paragraph("检测单位（盖章）", S_SIGN_L), "", ""],
         [Paragraph(org, S_SIGN), "", StampFlowable()],
         [Paragraph(f"签发日期：<u>{det_date}</u>", S_SIGN), "", ""]],
        colWidths=[8.0*cm, 3.2*cm, 4.4*cm])
    sign_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("ALIGN", (2,1), (2,2), "RIGHT"),
    ]))
    story.append(sign_tbl)

    # ---------- 页眉 / 页脚 / 水印 ----------
    def _draw_header_footer(canvas, doc):
        w, h = A4
        canvas.saveState()
        # 页眉：左侧徽章 + 平台名，右侧报告编号
        bw, bh = 1.05*cm, 1.05*cm
        bx, by = doc.leftMargin, h - 1.5*cm - bh/2
        canvas.setFillColor(C_PRIMARY)
        canvas.roundRect(bx, by, bw, bh, 4, stroke=0, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont("SimHei", 13)
        canvas.drawCentredString(bx + bw/2, by + bh/2 - 4.5, REPORT_ORG_SHORT)
        canvas.setFillColor(C_PRIMARY_D)
        canvas.setFont("SimHei", 11)
        canvas.drawString(bx + bw + 0.35*cm, by + bh/2 - 4.2, "人参重金属安全检测数据服务平台")
        canvas.setFillColor(C_MUTED)
        canvas.setFont("SimSun", 8)
        canvas.drawString(bx + bw + 0.35*cm, by + bh/2 - 13.5, "GINSENG HEAVY METAL SAFETY DATA SERVICE PLATFORM")
        # 右侧：报告编号
        canvas.setFillColor(C_TEXT)
        canvas.setFont("SimHei", 9.5)
        canvas.drawRightString(w - doc.rightMargin, by + bh/2 - 4.2,
                               f"报告编号：{report_id}")
        canvas.setFillColor(C_MUTED)
        canvas.setFont("SimSun", 8)
        canvas.drawRightString(w - doc.rightMargin, by + bh/2 - 13.5,
                               f"检测日期：{det_date}")
        # 页眉装饰线（放在徽章下方、标题上方，避免压到标题文字）
        line_y = h - (1.5*cm + bh/2 + 5)
        canvas.setStrokeColor(C_PRIMARY)
        canvas.setLineWidth(2.0)
        canvas.line(doc.leftMargin, line_y, w - doc.rightMargin, line_y)
        canvas.setStrokeColor(C_GOLD)
        canvas.setLineWidth(0.7)
        canvas.line(doc.leftMargin, line_y - 2.2, w - doc.rightMargin, line_y - 2.2)

        # 水印（对角淡字）
        canvas.saveState()
        canvas.translate(w/2, h/2)
        canvas.rotate(32)
        canvas.setFont("SimHei", 58)
        canvas.setFillColor(C_PRIMARY)
        canvas.setFillAlpha(0.028)
        canvas.drawCentredString(0, 0, "人参重金属安全检测")
        canvas.restoreState()

        # 页脚
        fy = 1.0*cm
        canvas.setStrokeColor(C_LINE)
        canvas.setLineWidth(0.8)
        canvas.line(doc.leftMargin, fy, w - doc.rightMargin, fy)
        canvas.setFillColor(C_MUTED)
        canvas.setFont("SimSun", 8.5)
        canvas.drawCentredString(w/2, fy - 10,
            f"{REPORT_ORG_SHORT} · 人参重金属安全检测数据服务平台  |  {org}  |  联系电话：0435-3208123")
        canvas.restoreState()

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2.0*cm, rightMargin=2.0*cm,
                            topMargin=1.5*cm, bottomMargin=1.25*cm,
                            title=f"人参重金属检测报告_{data.get('sample_id','')}",
                            author=REPORT_ORG)
    doc.build(story, onFirstPage=_draw_header_footer, onLaterPages=_draw_header_footer)
    buf.seek(0)
    return buf
