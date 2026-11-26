# -*- coding: utf-8 -*-
"""
把 template.html 里的 <!--CODE file start end--> 占位替换成带高亮和行号的代码块，
输出 index.html。代码直接读 src/ 下的原始文件，不手抄。
运行：python tools/build_site.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
TPL = os.path.join(ROOT, "template.html")
OUT = os.path.join(ROOT, "index.html")

KEYWORDS = {
    "def", "class", "return", "if", "elif", "else", "for", "while", "import", "from",
    "as", "with", "lambda", "in", "not", "and", "or", "is", "None", "True", "False",
    "pass", "assert", "raise", "try", "except", "finally", "global", "nonlocal",
    "yield", "del", "break", "continue", "async", "await",
}
BUILTINS = {
    "print", "len", "range", "int", "float", "str", "list", "dict", "tuple", "set",
    "super", "isinstance", "zip", "enumerate", "max", "min", "sum", "open", "type",
    "abs", "copy", "deepcopy",
}

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tokenize(code):
    """返回 [(text, cls)]，cls 为 None 表示普通文本。"""
    out = []
    i, n = 0, len(code)
    buf = []

    def flush():
        if buf:
            out.append(("".join(buf), None))
            buf.clear()

    while i < n:
        c = code[i]
        # 注释
        if c == "#":
            flush()
            j = code.find("\n", i)
            j = n if j < -1 or j == -1 else j
            out.append((code[i:j], "com"))
            i = j
            continue
        # 三引号字符串（含 docstring）
        if code.startswith('"""', i) or code.startswith("'''", i):
            flush()
            q = code[i:i + 3]
            j = code.find(q, i + 3)
            j = n if j == -1 else j + 3
            out.append((code[i:j], "str"))
            i = j
            continue
        # 普通字符串（考虑前缀 r/f/b)
        if c in "\"'":
            flush()
            start = i
            quote = c
            i += 1
            while i < n:
                if code[i] == "\\":
                    i += 2
                    continue
                if code[i] == quote:
                    i += 1
                    break
                i += 1
            out.append((code[start:i], "str"))
            continue
        # 装饰器
        if c == "@":
            flush()
            m = IDENT.match(code, i + 1)
            j = m.end() if m else i + 1
            out.append((code[i:j], "dec"))
            i = j
            continue
        # 标识符
        m = IDENT.match(code, i)
        if m:
            flush()
            word = m.group(0)
            if word in KEYWORDS:
                cls = "kw"
            elif word == "self":
                cls = "self"
            elif word in BUILTINS:
                cls = "bi"
            elif word[0].isupper():
                cls = "cls"
            else:
                # 后面紧跟 "(" 视为函数调用
                k = m.end()
                while k < n and code[k] == " ":
                    k += 1
                cls = "fn" if k < n and code[k] == "(" else None
            out.append((word, cls))
            i = m.end()
            continue
        # 数字
        if c.isdigit():
            flush()
            m = re.match(r"\d+\.?\d*(?:e[+-]?\d+)?", code[i:])
            out.append((m.group(0), "num"))
            i += len(m.group(0))
            continue
        buf.append(c)
        i += 1
    flush()
    return out


def render(code, start_line):
    tokens = tokenize(code)
    lines = [[]]
    for txt, cls in tokens:
        parts = txt.split("\n")
        for k, part in enumerate(parts):
            if part:
                lines[-1].append(f'<span class="tok-{cls}">{esc(part)}</span>' if cls else esc(part))
            if k < len(parts) - 1:
                lines.append([])
    rows = []
    for idx, chunks in enumerate(lines):
        no = start_line + idx
        body = "".join(chunks)
        rows.append(f'<span class="ln">{no}</span>{body}')
    return "\n".join(rows)


def build():
    tpl = open(TPL, encoding="utf-8").read()
    pat = re.compile(r"<!--CODE\s+(\S+)\s+(\d+)\s+(\d+)\s*-->")
    count = 0

    def repl(m):
        nonlocal count
        fname, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        path = os.path.join(SRC, fname)
        if not os.path.exists(path):
            sys.exit(f"缺少源文件: {path}")
        all_lines = open(path, encoding="utf-8").read().split("\n")
        if b > len(all_lines):
            sys.exit(f"{fname} 只有 {len(all_lines)} 行，越界引用到 {b}")
        snippet = "\n".join(all_lines[a - 1:b])
        count += 1
        return (
            '<div class="code reveal">\n'
            f'  <div class="code-head"><span class="fname">{fname}</span>'
            f'<span class="range">L{a}–L{b}</span>'
            '<button class="copy" type="button">复制</button></div>\n'
            f'  <pre><code>{render(snippet, a)}</code></pre>\n'
            "</div>"
        )

    html = pat.sub(repl, tpl)

    # 检查引用的资源是否存在
    for m in re.finditer(r'(?:src|href)="(assets/[^"]+|css/[^"]+|js/[^"]+)"', html):
        p = os.path.join(ROOT, m.group(1))
        if not os.path.exists(p):
            print("  ! 资源缺失:", m.group(1))

    open(OUT, "w", encoding="utf-8").write(html)
    print(f"index.html 生成完毕：{count} 个代码块，{len(html)} 字节")


if __name__ == "__main__":
    build()
