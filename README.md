# Transformer 拆解笔记

一个用来把 Transformer 拆开讲的静态网页：左边是原理，右边是源码，中间配可交互的示意图。
页面里的代码不是另抄的示例，而是直接读取 `src/` 下六个源文件的原文，按真实行号渲染。

> 在线访问：见仓库的 GitHub Pages 地址（`https://<用户名>.github.io/<仓库名>/`）。

## 页面结构

| 章节 | 讲什么 | 对应源码 |
| --- | --- | --- |
| 01 为什么要有 Transformer | RNN 的顺序依赖 vs 自注意力的全连接 | — |
| 02 整体架构 | 输入 → 编码器 → 解码器 → 输出 | `dm06_transformer.py` |
| 03 输入部分 | 词嵌入、位置编码（正弦公式） | `dm01_input.py` |
| 04 注意力机制 | 缩放点积注意力、掩码 | `dm02_selfattension.py` |
| 05 多头注意力 | 8 个头切分与合并 | `dm02_selfattension.py` |
| 06 前馈网络 | 512 → 2048 → 512 | `dm03_NormandAdd.py` |
| 07 层归一化与残差 | Post-LN / Pre-LN 的区别 | `dm03_NormandAdd.py` |
| 08 编码器 | 单层结构 + N=6 堆叠 | `dm04_Encoderlayer.py` |
| 09 解码器 | 两套掩码、交叉注意力、Generator | `dm05_decoderlayer.py` |
| 10 组装 | forward 的五行代码与形状流 | `dm06_transformer.py` |
| 11 运行与复现 | 依赖顺序与快速验证 | 全部 |
| 12 这份实现的边界 | 六条已知局限 | 全部 |

## 目录

```
.
├── index.html          # 成品页面（由 tools/build_site.py 生成，勿手改）
├── template.html       # 页面模板，正文都在这里
├── css/style.css       # 样式：主题变量、代码高亮配色、响应式
├── js/main.js          # 阅读进度条、章节高亮、复制按钮、渐入动画
├── assets/             # 9 张配图
│   ├── *.svg           # 架构图（脚本手绘，可无损缩放）
│   └── *.png           # 位置编码热力图、正弦曲线、注意力掩码
├── src/                # 六个源文件原文（页面代码块的唯一来源）
└── tools/
    ├── make_diagrams.py  # 生成 6 张 SVG 架构图
    ├── make_figures.py   # 生成 3 张 matplotlib 数据图
    └── build_site.py     # 读 src/ + template.html → index.html
```

## 本地预览

纯静态页面，不需要构建工具，也不依赖网络：

```bash
# 方式一：直接打开
open index.html

# 方式二：起个静态服务器（推荐，避免个别浏览器对本地文件的限制）
python -m http.server 8000
# 然后访问 http://localhost:8000
```

## 重新生成

装了 Python 3.8+ 即可，配图脚本额外需要 `matplotlib`：

```bash
pip install matplotlib          # 只有画数据图时需要
python tools/make_diagrams.py   # 重绘 6 张 SVG  → assets/
python tools/make_figures.py    # 重绘 3 张 PNG  → assets/
python tools/build_site.py      # 重新组装 index.html
```

- 改正文、改章节顺序：编辑 `template.html`，再跑 `build_site.py`。
  代码块位置用占位注释 `<!--CODE dm01_input.py 17 31-->` 标记，构建时替换为带行号和高亮的真实代码。
- 改源码：直接改 `src/*.py`，重跑 `build_site.py`，页面里的行号会跟着变。
- 改图：架构图在 `make_diagrams.py` 里用坐标手绘（保证文字和结构准确），数据图在 `make_figures.py` 里真实计算。

## 说明

- 页面是静态站点，无后端、无第三方脚本、无统计代码，所有资源都在仓库内。
- 示意图由脚本生成而非生成式模型绘制，目的是保证结构、维度标注与实际代码一致。
- 源码实现参考 The Annotated Transformer 的教学式写法，为「看得懂」而非「跑得快」服务，已知局限见页面第 12 章。
