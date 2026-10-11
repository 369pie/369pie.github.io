#!/usr/bin/env python3
"""Batch-update static Hugo output for 369pie portfolio branding."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HEADER = """<header id="header" class="clearfix site-header">
    <div class="container">
        <div class="col-group header-inner">
            <div class="site-name">
                <a id="logo" href="/">369pie</a>
                <p class="description">AI 架构 · 全栈交付 · 技术写作</p>
            </div>
            <button type="button" class="nav-toggle" aria-expanded="false" aria-label="打开菜单">菜单</button>
            <nav id="nav-menu" class="clearfix">
                <a href="/">首页</a>
                <a href="/resume/">简历</a>
                <a href="/categories/">归档</a>
                <a href="/about/">关于</a>
            </nav>
        </div>
    </div>
</header>"""

FOOTER = """<footer id="footer">
    <div class="container">
        &copy; 2019–2026 <a href="/">369pie</a>
        · <a href="https://github.com/369pie" target="_blank" rel="noopener noreferrer">GitHub</a>
        · Powered by <a rel="nofollow noopener" href="https://gohugo.io" target="_blank">Hugo</a>
    </div>
</footer>"""

HERO = """
                <section class="site-hero">
                    <p class="hero-role">Senior Engineer · AI 应用架构</p>
                    <h2>你好，我是 369pie</h2>
                    <p>十一年软件研发与架构经验，覆盖分布式系统、监控平台与全栈产品交付。近年专注 Agent / 大模型应用落地、Vibe Coding 独立交付与 ComfyUI 工作流教学。</p>
                    <p>本站保留历年技术笔记（Go、Rust、区块链、Python 等）；完整履历见<a href="/resume/">简历页</a>。</p>
                    <div class="hero-links">
                        <a href="/resume/">查看简历</a>
                        <a class="secondary" href="https://github.com/369pie" target="_blank" rel="noopener noreferrer">GitHub</a>
                    </div>
                </section>
"""

PORTFOLIO_CSS = '<link rel="stylesheet" href="/css/portfolio.css">'
SITE_JS = '<script type="text/javascript" src="/js/site.js" defer></script>'

HEADER_RE = re.compile(r"<header id=\"header\"[\s\S]*?</header>", re.MULTILINE)
FOOTER_RE = re.compile(r"<footer id=\"footer\">[\s\S]*?</footer>", re.MULTILINE)


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    text = text.replace("https://efvhi.github.io", "")
    text = text.replace("http://efvhi.github.io", "")
    text = text.replace("valar morghulis", "369pie")
    text = text.replace("we r here because we r not free", "AI 架构 · 全栈交付 · 技术写作")
    text = text.replace('content="efvhi"', 'content="369pie"')
    text = text.replace("By efvhi", "369pie")
    text = text.replace(
        "专注于IT互联网，包括但不限于Go语言(golang)、Rust、Android、Ios、Python、项目管理、抖音分析、软件架构、区块链等",
        "369pie 的技术作品集：AI 应用架构、Agent、分布式系统、Go/Rust/Python 与工程实践笔记",
    )
    text = text.replace(
        'name="Keywords" content="golang,go语言,go语言笔记,rust,博客,项目管理,python,软件架构,公众号,小程序,区块链"',
        'name="Keywords" content="369pie,AI架构,Agent,大模型,Go,Rust,Python,分布式系统,技术博客"',
    )

    if HEADER_RE.search(text):
        text = HEADER_RE.sub(HEADER, text, count=1)
    if FOOTER_RE.search(text):
        text = FOOTER_RE.sub(FOOTER, text, count=1)

    if PORTFOLIO_CSS not in text and "/css/style.css" in text:
        text = text.replace(
            '<link rel="stylesheet" href="/css/style.css">',
            '<link rel="stylesheet" href="/css/style.css">\n    ' + PORTFOLIO_CSS,
        )

    if SITE_JS not in text and "</body>" in text:
        text = text.replace("</body>", SITE_JS + "\n</body>")

    if path.name == "index.html" and path.parent == ROOT and '<section class="site-hero">' not in text:
        text = text.replace(
            '<div class="res-cons">\n                    \n                        <article class="post">',
            '<div class="res-cons">' + HERO + "\n                        <article class=\"post\">",
            1,
        )
        text = text.replace(
            "<title>369pie | AI 架构 · 全栈交付 · 技术写作</title>",
            "<title>369pie | AI 架构师与技术创作者</title>",
        )
        text = text.replace(
            'content="369pie | AI 架构 · 全栈交付 · 技术写作"',
            'content="369pie | AI 架构师与技术创作者"',
        )

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    count = 0
    for html in ROOT.rglob("*.html"):
        if "scripts" in html.parts:
            continue
        if process_file(html):
            count += 1
    print(f"Updated {count} HTML files")


if __name__ == "__main__":
    main()
