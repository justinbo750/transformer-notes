# -*- coding: utf-8 -*-
"""
生成网页所需的数据可视化配图（位置编码热力图 / 正弦曲线 / 注意力权重与掩码对比）。
运行：python tools/make_figures.py
输出：assets/pe_heatmap.png, assets/pe_curves.png, assets/attention_mask.png
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)

INK = "#0f172a"
MUTED = "#64748b"


# ---------------------------------------------------------------- 1. 位置编码
def positional_encoding(max_len=50, d_model=512):
    pe = np.zeros((max_len, d_model))
    pos = np.arange(0, max_len)[:, None]
    div_term = np.exp(np.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
    pe[:, 0::2] = np.sin(pos * div_term)
    pe[:, 1::2] = np.cos(pos * div_term)
    return pe


def fig_pe_heatmap():
    """整幅波浪图：不画坐标轴，轴标签在网页里用 HTML 排版。"""
    # 只画 sin 分量（偶数维）：cos 分量形状相同、相位差 90°，两列交替会让图案变成锯齿
    pe = positional_encoding(120, 512)[:, 0::2]
    fig = plt.figure(figsize=(9, 4), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(pe, aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1, interpolation="bilinear")
    ax.axis("off")
    fig.savefig(os.path.join(OUT, "pe_heatmap.png"), dpi=100, facecolor="white")
    plt.close(fig)


def fig_pe_curves():
    d_model, n = 512, 100
    pe = positional_encoding(n, d_model)
    dims = [0, 32, 96, 192]
    colors = ["#2563eb", "#0ea5e9", "#7c3aed", "#e11d48"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.5), dpi=220, sharey=True)
    for ax, offset, title in (
        (axes[0], 0, "偶数维：sin(pos × ω)，ω 随维度递减"),
        (axes[1], 1, "奇数维：cos(pos × ω)，与 sin 相差 90° 相位"),
    ):
        for c, i in zip(colors, dims):
            ax.plot(pe[:, i + offset], color=c, lw=1.6, alpha=0.9, label=f"i = {i + offset}")
        ax.set_title(title, fontsize=12, color=INK, pad=8)
        ax.set_xlabel("位置 pos", fontsize=10, color=MUTED)
        ax.grid(alpha=0.25, ls="--")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_xlim(0, n)
    axes[0].set_ylabel("编码值", fontsize=10, color=MUTED)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=9, frameon=False, ncol=4,
               loc="lower center", bbox_to_anchor=(0.5, -0.03), handlelength=1.6)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(os.path.join(OUT, "pe_curves.png"), facecolor="white", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- 2. 注意力
def scaled_dot_attention(seq_len=6, d_k=8, seed=7, causal=False):
    rng = np.random.default_rng(seed)
    q = rng.normal(size=(seq_len, d_k))
    k = rng.normal(size=(seq_len, d_k))
    scores = q @ k.T / math.sqrt(d_k)
    if causal:
        mask = np.tril(np.ones((seq_len, seq_len)))          # 只能看到自己与左侧
        scores = np.where(mask == 0, -1e9, scores)
    w = np.exp(scores - scores.max(axis=-1, keepdims=True))
    w = w / w.sum(axis=-1, keepdims=True)
    return scores, w


def fig_attention_mask():
    seq = 6
    _, w_full = scaled_dot_attention(seq, causal=False, seed=11)
    _, w_mask = scaled_dot_attention(seq, causal=True, seed=11)

    labels = ["<SOS>", "我", "爱", "学", "习", "</S>"]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3), dpi=220)
    for ax, w, title in (
        (axes[0], w_full, "自注意力：每个位置都能看到全部位置"),
        (axes[1], w_mask, "掩码注意力：只能看到自己与左侧历史"),
    ):
        im = ax.imshow(w, cmap="Blues", vmin=0, vmax=1)
        ax.set_xticks(range(seq))
        ax.set_yticks(range(seq))
        ax.set_xticklabels(labels, fontsize=10, color=INK)
        ax.set_yticklabels(labels, fontsize=10, color=INK)
        ax.set_xlabel("被关注的 Key 位置", fontsize=10, color=MUTED)
        ax.set_ylabel("发起查询的 Query 位置", fontsize=10, color=MUTED)
        ax.set_title(title, fontsize=11.5, color=INK, pad=10)
        ax.set_xticks(np.arange(-.5, seq, 1), minor=True)
        ax.set_yticks(np.arange(-.5, seq, 1), minor=True)
        ax.grid(which="minor", color="white", lw=2)
        ax.tick_params(which="minor", length=0)
        for i in range(seq):
            for j in range(seq):
                if w[i, j] < 0.01:
                    ax.text(j, i, "—", ha="center", va="center", color="#94a3b8", fontsize=9)
                else:
                    ax.text(j, i, f"{w[i, j]:.2f}", ha="center", va="center",
                            color="white" if w[i, j] > 0.55 else "#1e293b", fontsize=9)
        for s in ax.spines.values():
            s.set_color("#e2e8f0")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "attention_mask.png"), facecolor="white", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_pe_heatmap()
    fig_pe_curves()
    fig_attention_mask()
    print("figures written to", OUT)
