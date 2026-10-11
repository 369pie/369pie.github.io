#!/usr/bin/env python3
"""Generate 2026 AI articles and refresh listings/feeds."""

import html
import json
import re
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "scripts" / "posts_2026"
MANIFEST = POSTS_DIR / "manifest.json"
SITE = "https://369pie.github.io"
PER_PAGE = 10

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

RECENT_BLOCK_START = '<h3 class="widget-title">最近文章</h3>'
CATEGORY_COUNTS = {
    "前端": 1,
    "区块链": 2,
    "技术": 15,
    "数据库": 1,
    "编程语言": 7,
    "随笔": 4,
}


def parse_existing_post(slug: str) -> dict:
    path = ROOT / "post" / slug / "index.html"
    text = path.read_text(encoding="utf-8")
    title_m = re.search(r"<h1 class=\"post-title\">([^<]+)</h1>", text)
    if not title_m:
        title_m = re.search(r"<title>([^|]+)", text)
    iso_m = re.search(r'article:published_time" content="([^"]+)"', text)
    date_m = re.search(r'<date class="post-meta meta-date">\s*([^<]+)\s*</date>', text)
    cat_m = re.search(
        r'meta-category.*?/categories/[^"]+">([^<]+)</a>', text, re.S
    )
    excerpt_m = re.search(r'<div class="post-content">\s*([^<]{40,400})', text, re.S)
    title = html.unescape(title_m.group(1).strip()) if title_m else slug
    iso = iso_m.group(1).replace("&#43;", "+") if iso_m else "2015-01-01T00:00:00+08:00"
    display = date_m.group(1).strip() if date_m else ""
    category = cat_m.group(1).strip() if cat_m else "技术"
    cat_path = {
        "技术": "%E6%8A%80%E6%9C%AF",
        "随笔": "%E9%9A%8F%E7%AC%94",
        "编程语言": "%E7%BC%96%E7%A8%8B%E8%AF%AD%E8%A8%80",
        "区块链": "%E5%8C%BA%E5%9D%97%E9%93%BE",
        "前端": "%E5%89%8D%E7%AB%AF",
        "数据库": "%E6%95%B0%E6%8D%AE%E5%BA%93",
    }.get(category, "%E6%8A%80%E6%9C%AF")
    excerpt = re.sub(r"\s+", " ", excerpt_m.group(1).strip()) if excerpt_m else title
    return {
        "slug": slug,
        "title": title,
        "iso_date": iso,
        "display_date": display,
        "category": category,
        "category_path": cat_path,
        "tags": [],
        "excerpt": excerpt[:280] + ("……" if len(excerpt) > 280 else ""),
    }


def load_new_posts() -> list:
    items = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in items:
        body_path = POSTS_DIR / f"{item['slug']}.html"
        item["body_html"] = body_path.read_text(encoding="utf-8")
    return items


def sort_key(p: dict):
    raw = p["iso_date"].replace("&#43;", "+")
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return datetime(2015, 1, 1)


def listing_article(p: dict, full: bool = False) -> str:
    excerpt = html.escape(p["excerpt"])
    if full:
        excerpt = excerpt.replace("……", "")
    readmore = (
        f'\n                            <p class="readmore"><a href="/post/{p["slug"]}/">阅读全文</a></p>'
        if not full
        else ""
    )
    content = excerpt if not full else p.get("body_html", excerpt)
    return f"""
                        <article class="post">
                            <header>
                                <h1 class="post-title">
                                    <a href="/post/{p["slug"]}/" title="{html.escape(p["title"])}" >{html.escape(p["title"])}</a>
                                </h1>
                            </header>
                            <date class="post-meta meta-date">
                                {p["display_date"]}
                            </date>
                            
                            <div class="post-meta">
                                <span>|</span>
                                
                                <span class="meta-category"><a href="/categories/{p["category_path"]}">{p["category"]}</a></span>
                                
                            </div>
                            
                            <div class="post-content">
                                {content}
                            </div>{readmore}
                        </article>
                    """


def post_page(p: dict) -> str:
    tags_html = ""
    if p.get("tags"):
        lis = "\n".join(
            f'                                <li><a href="/tags/{t}">{t}</a></li>'
            for t in p["tags"]
        )
        tags_html = f"""
                        <div class="post-meta meta-tags">
                            
                            <ul class="clearfix">
{lis}
                                
                            </ul>
                            
                        </div>"""
    iso = p["iso_date"].replace("+", "&#43;")
    body = p.get("body_html", "")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>

    <meta charset="utf-8">
    <meta name="generator" content="Hugo 0.56.3" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>{html.escape(p["title"])} | 369pie</title>
    <meta property="og:title" content="{html.escape(p["title"])} - 369pie">
    <meta property="og:type" content="article">
        
    <meta property="article:published_time" content="{iso}">
        
        
    <meta property="article:modified_time" content="{iso}">
        
    <meta name="Keywords" content="369pie,AI架构,Agent,大模型,Go,Rust,Python,分布式系统,技术博客">
    <meta name="description" content="{html.escape(p["title"])}">
        
    <meta name="author" content="369pie">
    <meta property="og:url" content="/post/{p["slug"]}/">
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">

    <link rel="stylesheet" href="/css/normalize.css">
    
    <link rel="stylesheet" href="/css/style.css">
    <link rel="stylesheet" href="/css/portfolio.css">
    <script type="text/javascript" src="//cdn.bootcss.com/jquery/3.2.1/jquery.min.js"></script>

    


    
    
</head>

<body>
{HEADER}


<div id="body">
    <div class="container">
        <div class="col-group">

            <div class="col-8" id="main">
                <div class="res-cons">
                    <article class="post">
                        <header>
                            <h1 class="post-title">{html.escape(p["title"])}</h1>
                        </header>
                        <date class="post-meta meta-date">
                            {p["display_date"]}
                        </date>
                        
                        <div class="post-meta">
                            <span>|</span>
                            
                                <span class="meta-category"><a href="/categories/{p["category_path"]}">{p["category"]}</a></span>
                            
                        </div>
                        
                        
                        
                        <div class="post-content">
                            {body}
                        </div>

                        {tags_html}
                    </article>
                    
    
                </div>
            </div>
            <div id="secondary">
    <section class="widget">
        <form id="search" action="//www.google.com/search" method="get" accept-charset="utf-8" target="_blank" _lpchecked="1">
      
      <input type="text" name="q" maxlength="20" placeholder="Search">
      <input type="hidden" name="sitesearch" value="">
      <button type="submit" class="submit icon-search"></button>
</form>
    </section>
    
    <section class="widget">
        <h3 class="widget-title">最近文章</h3>
<ul class="widget-list" id="recent-posts-widget">
</ul>
    </section>

    

    <section class="widget">
        <h3 class="widget-title">分类</h3>
<ul class="widget-list">
    
    <li>
        <a href="/categories/%E5%89%8D%E7%AB%AF/">前端(1)</a>
    </li>
    
    <li>
        <a href="/categories/%E5%8C%BA%E5%9D%97%E9%93%BE/">区块链(2)</a>
    </li>
    
    <li>
        <a href="/categories/%E6%8A%80%E6%9C%AF/">技术(15)</a>
    </li>
    
    <li>
        <a href="/categories/%E6%95%B0%E6%8D%AE%E5%BA%93/">数据库(1)</a>
    </li>
    
    <li>
        <a href="/categories/%E7%BC%96%E7%A8%8B%E8%AF%AD%E8%A8%80/">编程语言(7)</a>
    </li>
    
    <li>
        <a href="/categories/%E9%9A%8F%E7%AC%94/">随笔(4)</a>
    </li>
    
</ul>
    </section>
</div>
        </div>
    </div>
</div>
{FOOTER}


<a id="rocket" href="#top"></a>
<script type="text/javascript" src="/js/totop.js?v=0.0.0" async=""></script>
<script type="text/javascript" src="/js/site.js" defer></script>
</body>
</html>
"""


def pagination(page: int, total_pages: int) -> str:
    if total_pages <= 1:
        return ""
    parts = ['\n                <div class="pagination">']
    if page > 1:
        prev_href = "/" if page == 2 else f"/page/{page - 1}/"
        parts.append(f'\n        <a href="{prev_href}">上一页</a>')
    parts.append("\n        <span class=\"page-number\">")
    for n in range(1, total_pages + 1):
        href = "/" if n == 1 else f"/page/{n}/"
        if n == page:
            parts.append(f'\n        <span class="current">{n}</span>')
        else:
            parts.append(f'\n        <a href="{href}">{n}</a>')
    parts.append("\n        </span>")
    if page < total_pages:
        parts.append(f'\n        <a href="/page/{page + 1}/">下一页</a>')
    parts.append("\n                </div>\n")
    return "".join(parts)


def build_home_page(posts: list, page_num: int, sidebar_recent: str) -> str:
    total_pages = (len(posts) + PER_PAGE - 1) // PER_PAGE
    start = (page_num - 1) * PER_PAGE
    chunk = posts[start : start + PER_PAGE]
    articles = "".join(listing_article(p) for p in chunk)
    hero = ""
    if page_num == 1:
        hero = """
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
    # Reuse index shell from current file for sidebar
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    sidebar_m = re.search(
        r"(<div id=\"secondary\">[\s\S]*?</div>\s*</div>\s*</div>\s*</div>)\s*</div>\s*<footer",
        index,
    )
    sidebar = sidebar_m.group(1) if sidebar_m else ""
    sidebar = re.sub(
        r"<ul class=\"widget-list\">[\s\S]*?</ul>",
        f"<ul class=\"widget-list\">\n{sidebar_recent}\n</ul>",
        sidebar,
        count=1,
    )
    pag = pagination(page_num, total_pages)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>

    <meta charset="utf-8">
    <meta name="generator" content="Hugo 0.56.3" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>369pie | AI 架构师与技术创作者</title>
    <meta property="og:title" content="369pie | AI 架构师与技术创作者">
    <meta property="og:type" content="website">
    <meta name="Keywords" content="369pie,AI架构,Agent,大模型,Go,Rust,Python,分布式系统,技术博客">
    <meta name="description" content="369pie 的技术作品集：AI 应用架构、Agent、分布式系统、Go/Rust/Python 与工程实践笔记">
    <meta property="og:url" content="https://369pie.github.io/">
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">

    <link rel="stylesheet" href="/css/normalize.css">
    
    <link rel="stylesheet" href="/css/style.css">
    <link rel="stylesheet" href="/css/portfolio.css">
    <link rel="alternate" type="application/rss+xml+xml" href="/index.xml" title="369pie" />
    <script type="text/javascript" src="//cdn.bootcss.com/jquery/3.2.1/jquery.min.js"></script>

    


    
    
</head>


<body>
{HEADER}


<div id="body">
    <div class="container">
        <div class="col-group">

            <div class="col-8" id="main">
                <div class="res-cons">
{hero}
{articles}
{pag}
                </div>
            </div>
            {sidebar}
{FOOTER}


<a id="rocket" href="#top"></a>
<script type="text/javascript" src="/js/totop.js?v=0.0.0" async=""></script>
<script type="text/javascript" src="/js/site.js" defer></script>
</body>
</html>
"""


def recent_list_html(posts: list, limit: int = 10) -> str:
    lines = []
    for p in posts[:limit]:
        t = html.escape(p["title"])
        lines.append(
            f'    <li>\n        <a href="/post/{p["slug"]}/" title="{t}">{t}</a>\n    </li>'
        )
    return "\n".join(lines)


def update_recent_in_file(path: Path, recent_html: str) -> None:
    text = path.read_text(encoding="utf-8")
    new_text, n = re.subn(
        r"(<h3 class=\"widget-title\">最近文章</h3>\s*<ul class=\"widget-list\">)[\s\S]*?(</ul>)",
        r"\1\n" + recent_html + r"\n\2",
        text,
        count=1,
    )
    if n:
        path.write_text(new_text, encoding="utf-8")


def category_listing(category_name: str, posts: list) -> None:
    cat_path = {
        "技术": "%E6%8A%80%E6%9C%AF",
        "随笔": "%E9%9A%8F%E7%AC%94",
    }[category_name]
    cat_posts = [p for p in posts if p["category"] == category_name]
    articles = ""
    for p in cat_posts:
        articles += f"""
                        <article class="post">
                            <header>
                                <h1 class="post-title">
                                    <a href="/post/{p["slug"]}/">{html.escape(p["title"])}</a>
                                </h1>
                            </header>
                            <date class="post-meta meta-date">
                                {p["display_date"]}
                            </date>
                            
                            <div class="post-meta meta-category">
                                |
                                
                                    <a href="/categories/{cat_path}">{category_name}</a>
                                
                            </div>
                            
                            <div class="post-content">
                                {html.escape(p["excerpt"])}
                                <p class="readmore"><a href="/post/{p["slug"]}/">阅读全文</a></p>
                            </div>
                        </article>
                    """
    cat_file = ROOT / "categories" / category_name / "index.html"
    text = cat_file.read_text(encoding="utf-8")
    text = re.sub(
        r"(<h3 class=\"archive-title\">[\s\S]*?</h3>\s*)\s*<article class=\"post\">[\s\S]*",
        r"\1" + articles,
        text,
        count=1,
    )
    count = len(cat_posts)
    text = re.sub(
        rf">{category_name}\(\d+\)</a>",
        f">{category_name}({count})</a>",
        text,
    )
    cat_file.write_text(text, encoding="utf-8")


def tag_listing(tag: str, posts: list) -> None:
    tagged = [p for p in posts if tag in p.get("tags", [])]
    if not tagged:
        return
    tag_dir = ROOT / "tags" / tag
    tag_dir.mkdir(parents=True, exist_ok=True)
    articles = ""
    for p in tagged:
        articles += f"""
                        <article class="post">
                            <header>
                                <h1 class="post-title">
                                    <a href="/post/{p["slug"]}/">{html.escape(p["title"])}</a>
                                </h1>
                            </header>
                            <date class="post-meta meta-date">
                                {p["display_date"]}
                            </date>
                            
                            <div class="post-meta meta-category">
                                |
                                
                                    <a href="/categories/{p["category_path"]}">{p["category"]}</a>
                                
                            </div>
                            
                            <div class="post-content">
                                {html.escape(p["excerpt"])}
                                <p class="readmore"><a href="/post/{p["slug"]}/">阅读全文</a></p>
                            </div>
                        </article>
                    """
    sample = (ROOT / "tags" / "go" / "index.html").read_text(encoding="utf-8")
    sample = re.sub(
        r"<span class=\"keyword\">go</span>",
        f'<span class="keyword">{tag}</span>',
        sample,
    )
    sample = re.sub(
        r"(<h3 class=\"archive-title\">[\s\S]*?</h3>\s*)\s*<article class=\"post\">[\s\S]*?(</div>\s*</div>\s*<div id=\"secondary\">)",
        r"\1" + articles + r"\2",
        sample,
        count=1,
    )
    (tag_dir / "index.html").write_text(sample, encoding="utf-8")
    (tag_dir / "page" / "1" / "index.html").parent.mkdir(parents=True, exist_ok=True)
    redirect = f'<!DOCTYPE html><html><head><title>/tags/{tag}/</title><link rel="canonical" href="/tags/{tag}/"/><meta name="robots" content="noindex"><meta charset="utf-8" /><meta http-equiv="refresh" content="0; url=/tags/{tag}/" /></head></html>'
    (tag_dir / "page" / "1" / "index.html").write_text(redirect, encoding="utf-8")


def update_rss(posts: list) -> None:
    for rss_path in [ROOT / "index.xml", ROOT / "post" / "index.xml"]:
        if not rss_path.exists():
            continue
        text = rss_path.read_text(encoding="utf-8")
        text = text.replace("valar morghulis", "369pie")
        items = []
        for p in posts[:15]:
            desc = html.escape(p["excerpt"])
            items.append(
                f"""
    <item>
      <title>{html.escape(p["title"])}</title>
      <link>{SITE}/post/{p["slug"]}/</link>
      <pubDate>{p["iso_date"].replace("+", " +")}</pubDate>
      
      <guid>{SITE}/post/{p["slug"]}/</guid>
      <description>{desc}</description>
    </item>"""
            )
        text = re.sub(
            r"<lastBuildDate>[^<]+</lastBuildDate>",
            f"<lastBuildDate>{posts[0]['iso_date'].replace('+', ' +')}</lastBuildDate>",
            text,
            count=1,
        )
        text = re.sub(r"\s*<item>[\s\S]*</item>", "".join(items), text)
        rss_path.write_text(text, encoding="utf-8")


def update_sitemap(posts: list) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    for p in posts[:6]:
        loc = f"{SITE}/post/{p['slug']}/"
        if loc in text:
            continue
        entry = f"""
  <url>
    <loc>{loc}</loc>
    <lastmod>{p['iso_date'][:10]}T00:00:00+08:00</lastmod>
  </url>
"""
        text = text.replace("</urlset>", entry + "\n</urlset>")
    path.write_text(text, encoding="utf-8")


def patch_category_counts_in_html(recent_html: str) -> None:
    for html_file in ROOT.rglob("*.html"):
        if "scripts" in html_file.parts:
            continue
        text = html_file.read_text(encoding="utf-8")
        orig = text
        text = text.replace("技术(10)", "技术(15)")
        text = text.replace("随笔(3)", "随笔(4)")
        if RECENT_BLOCK_START in text:
            text, _ = re.subn(
                r"(<h3 class=\"widget-title\">最近文章</h3>\s*<ul class=\"widget-list\">)[\s\S]*?(</ul>)",
                r"\1\n" + recent_html + r"\n\2",
                text,
                count=1,
            )
        if text != orig:
            html_file.write_text(text, encoding="utf-8")


def main():
    new_slugs = {p["slug"] for p in json.loads(MANIFEST.read_text())}
    existing = []
    for slug_dir in sorted((ROOT / "post").iterdir()):
        if not slug_dir.is_dir() or slug_dir.name == "index.xml":
            continue
        slug = slug_dir.name
        if slug in new_slugs:
            continue
        existing.append(parse_existing_post(slug))

    new_posts = load_new_posts()
    all_posts = sorted(new_posts + existing, key=sort_key, reverse=True)
    recent_html = recent_list_html(all_posts)

    for p in new_posts:
        out = ROOT / "post" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        page_html = post_page(p)
        page_html = page_html.replace(
            '<ul class="widget-list" id="recent-posts-widget">\n</ul>',
            f"<ul class=\"widget-list\">\n{recent_html}\n</ul>",
        )
        out.write_text(page_html, encoding="utf-8")

    total_pages = (len(all_posts) + PER_PAGE - 1) // PER_PAGE
    ROOT.joinpath("index.html").write_text(
        build_home_page(all_posts, 1, recent_html), encoding="utf-8"
    )
    for n in range(2, total_pages + 1):
        page_dir = ROOT / "page" / str(n)
        page_dir.mkdir(parents=True, exist_ok=True)
        # clone sidebar from page/2 for non-home pages
        shell = build_home_page(all_posts, n, recent_html)
        shell = shell.replace(hero if (hero := "") else "", "")  # no-op safeguard
        page_dir.joinpath("index.html").write_text(shell, encoding="utf-8")

    category_listing("技术", all_posts)
    category_listing("随笔", all_posts)

    tags_needed = {"agent", "aigc", "llm"}
    for t in tags_needed:
        tag_listing(t, all_posts)

    update_rss(all_posts)
    update_sitemap(all_posts)
    patch_category_counts_in_html(recent_html)

    print(f"Published {len(new_posts)} posts; total {len(all_posts)} posts, {total_pages} pages.")


if __name__ == "__main__":
    main()
