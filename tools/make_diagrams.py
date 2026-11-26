# -*- coding: utf-8 -*-
"""
生成网页所需的架构示意 SVG（矢量、可缩放、文字可选中）。
运行：python tools/make_diagrams.py
输出：assets/arch-overall.svg, block-encoder.svg, block-decoder.svg,
      attn-scaled.svg, multihead.svg, rnn-vs-transformer.svg
"""
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)

FONT = "'Inter','Noto Sans SC',system-ui,-apple-system,'PingFang SC','Microsoft YaHei',sans-serif"

INK = "#0f172a"
SUB = "#475569"
MUTED = "#94a3b8"
LINE = "#cbd5e1"
BG = "#ffffff"

BLUE, BLUE_BG, BLUE_LT = "#2563eb", "#eff6ff", "#bfdbfe"
PURPLE, PURPLE_BG, PURPLE_LT = "#7c3aed", "#f5f3ff", "#ddd6fe"
TEAL, TEAL_BG, TEAL_LT = "#0891b2", "#ecfeff", "#a5f3fc"
AMBER, AMBER_BG, AMBER_LT = "#b45309", "#fffbeb", "#fde68a"
SLATE_BG, SLATE_LT = "#f1f5f9", "#e2e8f0"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h, y0=0):
    mk = ""
    for name, color in (("ar", SUB), ("ar-blue", BLUE), ("ar-purple", PURPLE),
                        ("ar-teal", TEAL), ("ar-amber", AMBER), ("ar-muted", MUTED)):
        mk += (f'  <marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" '
               f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
               f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>\n')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {y0} {w} {h}" width="{w}" height="{h}"'
            f' font-family="{FONT}">\n<defs>\n{mk}</defs>\n'
            f'<rect y="{y0}" width="{w}" height="{h}" fill="{BG}"/>\n')


def text(x, y, s, fs=13, color=INK, anchor="middle", weight="500", opacity=1.0, ls=0):
    sp = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" font-size="{fs}" fill="{color}" text-anchor="{anchor}" '
            f'font-weight="{weight}" opacity="{opacity}"{sp}>{esc(s)}</text>\n')


def multiline(x, y, lines, fs=13, lh=1.32, **kw):
    n = len(lines)
    total = (n - 1) * fs * lh
    out = ""
    for i, ln in enumerate(lines):
        out += text(x, y - total / 2 + i * fs * lh + fs * 0.35, ln, fs=fs, **kw)
    return out


def rbox(x, y, w, h, lines, fill=BG, stroke=LINE, fs=13, color=INK,
         weight="600", rx=10, sw=1.5, dash=""):
    if isinstance(lines, str):
        lines = [lines]
    longest = max(len(s) for s in lines)
    while longest * fs * 1.02 > w - 20 and fs > 8:
        fs -= 0.5
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
           f'stroke="{stroke}" stroke-width="{sw}"{d}/>\n')
    return out + multiline(x + w / 2, y + h / 2, lines, fs=fs, color=color, weight=weight)


def arrow(x1, y1, x2, y2, color=SUB, w=1.6, dash="", marker="ar"):
    d = (f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" '
         f'stroke-width="{w}" marker-end="url(#{marker})"')
    if dash:
        d += f' stroke-dasharray="{dash}"'
    return d + "/>\n"


def poly(points, color=SUB, w=1.6, marker="ar", dash=""):
    d = " ".join(f"{'M' if i == 0 else 'L'}{p[0]},{p[1]}" for i, p in enumerate(points))
    s = (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
         f'marker-end="url(#{marker})"')
    if dash:
        s += f' stroke-dasharray="{dash}"'
    return s + "/>\n"


def plus(cx, cy, r=13, color=AMBER_LT, fill=BG, fs=15, stroke=AMBER):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n'
            + text(cx, cy + fs * 0.34, "+", fs=fs, color=stroke, weight="600"))


# --------------------------------------------------------------------- 1. 整体架构
def arch_overall():
    W, H = 1400, 750
    s = header(W, H, 100)

    enc_x, enc_y, enc_w, enc_h = 260, 250, 320, 430
    dec_x, dec_w = 860, 320
    dec_h = 430
    ecx = enc_x + enc_w / 2          # 420
    dcx = dec_x + dec_w / 2          # 1020

    # 堆叠暗示
    for i, op in ((2, 0.10), (1, 0.18)):
        s += (f'<rect x="{enc_x + i * 10}" y="{enc_y - i * 10}" width="{enc_w}" height="{enc_h}" rx="16" '
              f'fill="{BLUE_BG}" stroke="{BLUE_LT}" stroke-width="1.5" opacity="{op}"/>\n')
        s += (f'<rect x="{dec_x + i * 10}" y="{enc_y - i * 10}" width="{dec_w}" height="{dec_h}" rx="16" '
              f'fill="{PURPLE_BG}" stroke="{PURPLE_LT}" stroke-width="1.5" opacity="{op}"/>\n')
    s += (f'<rect x="{enc_x}" y="{enc_y}" width="{enc_w}" height="{enc_h}" rx="16" fill="{BLUE_BG}" '
          f'stroke="{BLUE_LT}" stroke-width="2"/>\n')
    s += (f'<rect x="{dec_x}" y="{enc_y}" width="{dec_w}" height="{dec_h}" rx="16" fill="{PURPLE_BG}" '
          f'stroke="{PURPLE_LT}" stroke-width="2"/>\n')

    s += text(enc_x + 20, enc_y + 28, "编码器层 × 6", fs=14, color=BLUE, anchor="start", weight="700", ls=1)
    s += text(dec_x + 20, enc_y + 28, "解码器层 × 6", fs=14, color=PURPLE, anchor="start", weight="700", ls=1)

    # 编码器内部
    bx, bw = enc_x + 34, enc_w - 68
    enc_items = [(306, 64, "多头自注意力", TEAL_BG, TEAL, True),
                 (398, 38, "加 & 归一化", SLATE_BG, LINE, False),
                 (462, 64, "前馈全连接", TEAL_BG, TEAL, True),
                 (554, 38, "加 & 归一化", SLATE_BG, LINE, False)]
    for y, h, label, fill, stroke, strong in enc_items:
        s += rbox(bx, y, bw, h, label, fill=fill, stroke=stroke, fs=18 if strong else 15,
                  color=INK if strong else SUB)
    s += arrow(ecx, 665, ecx, 594, color=BLUE, marker="ar-blue")
    s += arrow(ecx, 554, ecx, 528, color=BLUE, marker="ar-blue")
    s += arrow(ecx, 462, ecx, 438, color=BLUE, marker="ar-blue")
    s += arrow(ecx, 398, ecx, 372, color=BLUE, marker="ar-blue")
    s += arrow(ecx, 306, ecx, 216, color=BLUE, w=1.8, marker="ar-blue")

    # 解码器内部
    ddx, dbw = dec_x + 34, dec_w - 68
    dec_items = [(282, 48, "掩码多头自注意力", TEAL_BG, TEAL, True),
                 (344, 30, "加 & 归一化", SLATE_BG, LINE, False),
                 (388, 48, "多头交叉注意力", TEAL_BG, TEAL, True),
                 (450, 30, "加 & 归一化", SLATE_BG, LINE, False),
                 (494, 48, "前馈全连接", TEAL_BG, TEAL, True),
                 (556, 30, "加 & 归一化", SLATE_BG, LINE, False)]
    for y, h, label, fill, stroke, strong in dec_items:
        s += rbox(ddx, y, dbw, h, label, fill=fill, stroke=stroke, fs=18 if strong else 15,
                  color=INK if strong else SUB)
    s += arrow(dcx, 665, dcx, 588, color=PURPLE, marker="ar-purple")
    s += arrow(dcx, 556, dcx, 544, color=PURPLE, marker="ar-purple")
    s += arrow(dcx, 494, dcx, 482, color=PURPLE, marker="ar-purple")
    s += arrow(dcx, 450, dcx, 438, color=PURPLE, marker="ar-purple")
    s += arrow(dcx, 388, dcx, 376, color=PURPLE, marker="ar-purple")
    s += arrow(dcx, 344, dcx, 332, color=PURPLE, marker="ar-purple")
    s += arrow(dcx, 282, dcx, 216, color=PURPLE, w=1.8, marker="ar-purple")

    # 交叉注意力：编码器输出 -> 解码器
    cross_y = 412
    s += arrow(enc_x + enc_w + 8, cross_y, dec_x - 10, cross_y, color=PURPLE, w=2, marker="ar-purple")
    s += text((enc_x + enc_w + dec_x) / 2, cross_y - 14, "编码器输出作为 K, V", fs=14, color=PURPLE, weight="600")

    # 底部输入
    row_y, row_h = 750, 48
    s += rbox(enc_x - 186, row_y, 150, row_h, "输入序列", fill=SLATE_BG, stroke=LINE, fs=12, color=SUB)
    s += text(enc_x - 111, row_y + 70, "我 / 爱 / 学习", fs=12, color=MUTED)
    s += arrow(enc_x - 34, row_y + 24, enc_x - 4, row_y + 24, color=SUB, w=1.6)
    s += rbox(enc_x, row_y, 200, row_h, "输入嵌入", fill=BLUE_BG, stroke=BLUE_LT, fs=15.5, color=BLUE)

    s += arrow(ecx, row_y, ecx, 731, color=BLUE, marker="ar-blue")
    s += plus(ecx, 715, r=14)
    s += text(ecx + 22, 719, "位置编码 PE", fs=13.5, color=SUB, anchor="start", weight="600")
    s += arrow(ecx, 699, ecx, 669, color=BLUE, marker="ar-blue")

    s += rbox(dec_x - 186, row_y, 150, row_h, "输出序列（右移）", fill=SLATE_BG, stroke=LINE, fs=13, color=SUB)
    s += text(dec_x - 111, row_y + 70, "<SOS> / 我 / 爱", fs=12, color=MUTED)
    s += arrow(dec_x - 34, row_y + 24, dec_x - 4, row_y + 24, color=SUB, w=1.6)
    s += rbox(dec_x, row_y, 200, row_h, "输出嵌入", fill=PURPLE_BG, stroke=PURPLE_LT, fs=15.5, color=PURPLE)
    s += arrow(dcx, row_y, dcx, 731, color=PURPLE, marker="ar-purple")
    s += plus(dcx, 715, r=14, stroke=PURPLE, color=PURPLE_LT)
    s += text(dcx + 22, 719, "位置编码 PE", fs=13.5, color=SUB, anchor="start", weight="600")
    s += arrow(dcx, 699, dcx, 669, color=PURPLE, marker="ar-purple")

    # 顶部输出层
    s += arrow(dcx, 216, dcx, 168, color=PURPLE, w=1.8, marker="ar-purple")
    s += rbox(dcx - 100, 112, 200, 54, "线性 + Softmax", fill=AMBER_BG, stroke=AMBER_LT, fs=16.5, color=AMBER)
    s += text(dcx + 114, 134, "→ 词表概率分布", fs=13.5, color=MUTED, anchor="start")
    s += text(dcx + 114, 154, "argmax → 下一个词", fs=13.5, color=MUTED, anchor="start")

    # 顶部引言
    s += text(enc_x - 30, 120, "一句话：编码器把输入读成一组上下文向量，解码器据此一个词一个词地生成输出。",
              fs=17, color=INK, anchor="start", weight="700")
    s += text(enc_x - 30, 148, "六层「自注意力 → 残差归一化 → 前馈 → 残差归一化」堆叠，全程没有循环，因此整句可以并行计算。",
              fs=12, color=SUB, anchor="start", weight="400")

    s += "</svg>\n"
    open(os.path.join(OUT, "arch-overall.svg"), "w", encoding="utf-8").write(s)


# --------------------------------------------------------------------- 2. 编码器层
def block_encoder():
    W, H = 660, 560
    s = header(W, H)
    cx = 250
    norm_w = 260
    s += text(cx, 52, "输出", fs=11.5, color=MUTED)
    s += arrow(cx, 64, cx, 90, color=SUB, w=1.8)
    s += rbox(cx - norm_w / 2, 94, norm_w, 36, "层归一化 LayerNorm", fill=SLATE_BG, stroke=LINE, fs=12, color=SUB)
    s += arrow(cx, 136, cx, 164, color=SUB, w=1.8)
    s += rbox(cx - norm_w / 2, 168, norm_w, 86, ["前馈全连接 FFN", "Linear 512 → 1024 → 512"], fill=TEAL_BG, stroke=TEAL, fs=13.5, color=INK)
    s += arrow(cx, 260, cx, 288, color=SUB, w=1.8)
    s += rbox(cx - norm_w / 2, 292, norm_w, 36, "层归一化 LayerNorm", fill=SLATE_BG, stroke=LINE, fs=12, color=SUB)
    s += arrow(cx, 334, cx, 362, color=SUB, w=1.8)
    s += rbox(cx - norm_w / 2, 366, norm_w, 86, ["多头自注意力", "8 个头，d_k = 64"], fill=TEAL_BG, stroke=TEAL, fs=13.5, color=INK)
    s += arrow(cx, 458, cx, 486, color=SUB, w=1.8)
    s += text(cx, 506, "输入 X  [2, 5, 512]", fs=11.5, color=MUTED)

    rx = 450                        # 残差支路
    s += poly([(cx, 476), (rx, 476), (rx, 112), (cx + norm_w / 2 + 32, 112)], color=AMBER, w=1.6, marker="ar-amber")
    s += plus(cx + norm_w / 2 + 18, 112, r=13)
    s += poly([(cx, 356), (rx, 356), (rx, 310), (cx + norm_w / 2 + 32, 310)], color=AMBER, w=1.6, marker="ar-amber")
    s += plus(cx + norm_w / 2 + 18, 310, r=13)
    s += text(rx + 16, 300, "残差", fs=10.5, color=AMBER, anchor="start", weight="600", opacity=0.85)
    s += text(cx, 546, "x + Dropout( Norm( 子层(x) ) )", fs=11, color=MUTED)
    s += "</svg>\n"
    open(os.path.join(OUT, "block-encoder.svg"), "w", encoding="utf-8").write(s)


# --------------------------------------------------------------------- 3. 解码器层
def block_decoder():
    W, H = 780, 720
    s = header(W, H)
    cx = 250
    nw = 260
    s += text(cx, 52, "输出", fs=11.5, color=MUTED)
    s += arrow(cx, 64, cx, 88, color=SUB, w=1.8)
    s += rbox(cx - nw / 2, 92, nw, 34, "层归一化 LayerNorm", fill=SLATE_BG, stroke=LINE, fs=12, color=SUB)
    s += arrow(cx, 132, cx, 158, color=SUB, w=1.8)
    s += rbox(cx - nw / 2, 162, nw, 84, ["前馈全连接 FFN", "512 → 2048 → 512"], fill=TEAL_BG, stroke=TEAL, fs=13.5, color=INK)
    s += arrow(cx, 252, cx, 278, color=SUB, w=1.8)
    s += rbox(cx - nw / 2, 282, nw, 34, "层归一化 LayerNorm", fill=SLATE_BG, stroke=LINE, fs=12, color=SUB)
    s += arrow(cx, 322, cx, 348, color=SUB, w=1.8)
    s += rbox(cx - nw / 2, 352, nw, 84, ["多头交叉注意力", "Q 来自解码器 · K, V 来自编码器"], fill=PURPLE_BG, stroke=PURPLE, fs=12.5, color=INK)
    s += arrow(cx, 442, cx, 468, color=SUB, w=1.8)
    s += rbox(cx - nw / 2, 472, nw, 34, "层归一化 LayerNorm", fill=SLATE_BG, stroke=LINE, fs=12, color=SUB)
    s += arrow(cx, 512, cx, 538, color=SUB, w=1.8)
    s += rbox(cx - nw / 2, 542, nw, 84, ["掩码多头自注意力", "每个位置只能看到左侧历史"], fill=TEAL_BG, stroke=TEAL, fs=12.5, color=INK)
    s += arrow(cx, 632, cx, 658, color=SUB, w=1.8)
    s += text(cx, 678, "输入 y  [2, 5, 512]", fs=11.5, color=MUTED)

    # 残差支路
    rx = 450
    s += poly([(cx, 650), (rx, 650), (rx, 109), (cx + nw / 2 + 32, 109)], color=AMBER, w=1.6, marker="ar-amber")
    s += plus(cx + nw / 2 + 18, 109, r=13)
    for y in (299, 489):
        s += poly([(cx, 650), (rx, 650), (rx, y), (cx + nw / 2 + 32, y)], color=AMBER, w=1.6, marker="ar-amber")
        s += plus(cx + nw / 2 + 18, y, r=13)
    s += text(rx + 16, 470, "残差", fs=10.5, color=AMBER, anchor="start", weight="600", opacity=0.85)

    # 编码器输出
    s += arrow(700, 394, cx + nw / 2 + 4, 394, color=PURPLE, w=1.8, marker="ar-purple")
    s += text(700, 376, "编码器输出", fs=11.5, color=PURPLE, anchor="end", weight="600")
    s += "</svg>\n"
    open(os.path.join(OUT, "block-decoder.svg"), "w", encoding="utf-8").write(s)


# --------------------------------------------------------------------- 4. 缩放点积注意力
def attn_scaled():
    W, H = 1160, 320
    s = header(W, H, 108)
    mid = 250

    s += rbox(56, 130, 122, 50, "Q", fill=BLUE_BG, stroke=BLUE, fs=17, color=BLUE)
    s += rbox(56, 320, 122, 50, "K", fill=BLUE_BG, stroke=BLUE, fs=17, color=BLUE)
    s += text(117, 200, "查询：我要找什么", fs=11, color=MUTED)
    s += text(117, 392, "键：每个位置的标签", fs=11, color=MUTED)

    c1 = 248
    s += arrow(180, 158, c1 - 20, mid - 10, color=SUB, w=1.6)
    s += arrow(180, 342, c1 - 20, mid + 10, color=SUB, w=1.6)
    s += (f'<circle cx="{c1}" cy="{mid}" r="22" fill="{BLUE_BG}" stroke="{BLUE_LT}" stroke-width="1.6"/>\n')
    s += text(c1, mid + 6, "×", fs=17, color=BLUE, weight="700")
    s += text(c1, mid + 44, "MatMul", fs=11, color=MUTED)

    s += arrow(c1 + 22, mid, 340, mid, color=SUB, w=1.6)
    s += rbox(342, mid - 30, 148, 60, ["缩放", "1 / √d_k"], fill=SLATE_BG, stroke=LINE, fs=13, color=SUB)
    s += arrow(490, mid, 528, mid, color=SUB, w=1.6)
    s += rbox(530, mid - 30, 148, 60, ["掩码（可选）", "padding / 未来信息"], fill=BG, stroke=MUTED, fs=11, color=SUB, dash="5 4")
    s += arrow(678, mid, 716, mid, color=SUB, w=1.6)
    s += rbox(718, mid - 30, 118, 60, "Softmax", fill=AMBER_BG, stroke=AMBER_LT, fs=14, color=AMBER)
    s += text(772, mid + 52, "权重 [2, 8, 5, 5]", fs=11, color=MUTED)

    c2 = 900
    s += arrow(836, mid, c2 - 22, mid, color=SUB, w=1.6)
    s += (f'<circle cx="{c2}" cy="{mid}" r="22" fill="{BLUE_BG}" stroke="{BLUE_LT}" stroke-width="1.6"/>\n')
    s += text(c2, mid + 6, "×", fs=17, color=BLUE, weight="700")
    s += text(c2 + 30, mid + 46, "MatMul", fs=11, color=MUTED, anchor="start")

    s += rbox(838, 320, 122, 50, "V", fill=BLUE_BG, stroke=BLUE, fs=17, color=BLUE)
    s += text(899, 392, "值：被加权的内容", fs=11, color=MUTED)
    s += arrow(884, 318, 884, mid + 26, color=SUB, w=1.6)

    s += arrow(c2 + 22, mid, 1042, mid, color=BLUE, w=1.8, marker="ar-blue")
    s += text(1052, 244, "注意力输出", fs=12.5, color=BLUE, anchor="start", weight="600")
    s += text(1052, 264, "[2, 5, 512]", fs=10.5, color=MUTED, anchor="start")
    s += "</svg>\n"
    open(os.path.join(OUT, "attn-scaled.svg"), "w", encoding="utf-8").write(s)


# --------------------------------------------------------------------- 5. 多头注意力
def multihead():
    W, H = 1210, 356
    s = header(W, H, 70)

    s += rbox(40, 196, 116, 60, ["输入 X", "[2, 5, 512]"], fill=SLATE_BG, stroke=LINE, fs=11, color=SUB)
    s += arrow(158, 226, 186, 226, color=SUB, w=1.6)

    s += (f'<rect x="188" y="120" width="176" height="212" rx="14" fill="{BLUE_BG}" '
          f'stroke="{BLUE_LT}" stroke-width="1.5"/>\n')
    s += text(276, 142, "线性投影", fs=12, color=BLUE, weight="700", ls=1)
    for n, y in (("W_Q", 152), ("W_K", 205), ("W_V", 258)):
        s += rbox(202, y, 148, 46, [n + " · Linear(512, 512)"], fill=BG, stroke=BLUE_LT, fs=11.5, color=BLUE, rx=8)
    s += arrow(366, 226, 404, 226, color=SUB, w=1.7)

    hx0, hw, gap = 406, 116, 16
    s += (f'<rect x="{hx0 - 10}" y="80" width="{4 * hw + 3 * gap + 20}" height="300" rx="16" '
          f'fill="#f8fafc" stroke="{SLATE_LT}" stroke-width="1.5"/>\n')
    s += text(hx0 + (4 * hw + 3 * gap) / 2, 104, "8 个注意力头 · 并行计算", fs=12, color=MUTED, weight="600", ls=0.5)

    for i in range(4):
        x = hx0 + i * (hw + gap)
        s += (f'<rect x="{x}" y="120" width="{hw}" height="234" rx="12" fill="{TEAL_BG}" '
              f'stroke="{TEAL_LT}" stroke-width="1.5"/>\n')
        s += text(x + hw / 2, 142, f"头 {i + 1}", fs=13, color=TEAL, weight="700")
        s += rbox(x + 12, 154, hw - 24, 52, ["Q · Kᵀ", "缩放 1/√d_k"], fill=BG, stroke=LINE, fs=11, color=SUB, rx=8)
        s += rbox(x + 12, 226, hw - 24, 38, "Softmax", fill=AMBER_BG, stroke=AMBER_LT, fs=11, color=AMBER, rx=8)
        s += rbox(x + 12, 284, hw - 24, 52, ["权重 × V", "得到头输出"], fill=BG, stroke=LINE, fs=11, color=SUB, rx=8)
        s += arrow(x + hw / 2, 206, x + hw / 2, 224, color=SUB, w=1.2)
        s += arrow(x + hw / 2, 264, x + hw / 2, 282, color=SUB, w=1.2)
    s += text(hx0 + (4 * hw + 3 * gap) / 2, 404, "…… 共 8 个头，每个头只看 64 维子空间", fs=12, color=MUTED)

    s += arrow(hx0 + 4 * hw + 3 * gap + 4, 226, 958, 226, color=TEAL, w=1.7, marker="ar-teal")
    s += rbox(958, 146, 156, 160, ["拼接 Concat", "8 × 64 = 512", "线性 W_O"], fill=PURPLE_BG, stroke=PURPLE_LT, fs=12.5, color=PURPLE)
    s += arrow(1114, 226, 1146, 226, color=BLUE, w=1.6, marker="ar-blue")
    s += text(1152, 212, "输出", fs=12.5, color=BLUE, anchor="start", weight="600")
    s += text(1152, 232, "[2, 5, 512]", fs=9.5, color=MUTED, anchor="start")
    s += "</svg>\n"
    open(os.path.join(OUT, "multihead.svg"), "w", encoding="utf-8").write(s)


# --------------------------------------------------------------------- 6. RNN vs Transformer
def rnn_vs():
    W, H = 1000, 520
    s = header(W, H)

    s += text(50, 52, "RNN：逐时刻串行", fs=14.5, color=INK, anchor="start", weight="700")
    s += text(50, 78, "h₃ 必须等 h₁、h₂ 算完；长距离信息要沿链条一路传递，容易衰减。", fs=11,
              color=SUB, anchor="start", weight="400")

    xs = [110, 280, 450, 620]
    for i, x in enumerate(xs):
        if i:
            s += arrow(xs[i - 1] + 32, 170, x - 34, 170, color=MUTED, w=1.5, marker="ar-muted")
        s += (f'<circle cx="{x}" cy="170" r="32" fill="{BLUE_BG}" stroke="{BLUE}" stroke-width="1.6"/>\n')
        s += text(x, 176, f"h{i + 1}", fs=12.5, color=BLUE, weight="700")
        s += rbox(x - 34, 224, 68, 28, f"词 {i + 1}", fill=BG, stroke=LINE, fs=10, color=SUB, rx=6)
        s += arrow(x, 222, x, 206, color=MUTED, w=1.2, marker="ar-muted")

    s += f'<line x1="50" y1="290" x2="950" y2="290" stroke="{SLATE_LT}" stroke-width="1.5"/>\n'

    s += text(50, 336, "Transformer：整句并行", fs=14.5, color=INK, anchor="start", weight="700")
    s += text(50, 362, "所有位置同时进入注意力层，任意两个词之间都只隔一步。", fs=11, color=SUB,
              anchor="start", weight="400")

    top = [160, 340, 520, 700]
    bot = [160, 340, 520, 700]
    for by in bot:
        for ty in top:
            s += f'<path d="M{by},470 L{ty},408" stroke="{TEAL_LT}" stroke-width="1.4" stroke-opacity="0.9"/>\n'
    for ty in top:
        s += f'<circle cx="{ty}" cy="400" r="11" fill="{TEAL}"/>\n'
    for i, by in enumerate(bot):
        s += f'<circle cx="{by}" cy="478" r="11" fill="{BLUE}"/>\n'
        s += rbox(by - 32, 496, 64, 24, f"词 {i + 1}", fill=BG, stroke=LINE, fs=9.5, color=SUB, rx=6)
    s += text(760, 396, "上下文表示", fs=10.5, color=TEAL, anchor="start", weight="600")
    s += text(760, 482, "输入 token", fs=10.5, color=BLUE, anchor="start", weight="600")
    s += "</svg>\n"
    open(os.path.join(OUT, "rnn-vs-transformer.svg"), "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    arch_overall()
    block_encoder()
    block_decoder()
    attn_scaled()
    multihead()
    rnn_vs()
    print("svg diagrams written to", OUT)
