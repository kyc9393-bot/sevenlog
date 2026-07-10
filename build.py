#!/usr/bin/env python3
"""세븐로그 정적 사이트 빌더.

사용법:
    python3 build.py            # _site/ 폴더에 사이트 생성
    python3 build.py --serve    # 빌드 후 로컬 미리보기 서버 실행 (http://localhost:8000)

의존성: pip install markdown
"""
import json
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
KST = timezone(timedelta(hours=9))

MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists", "smarty"]

with open(ROOT / "config.json", encoding="utf-8") as f:
    CFG = json.load(f)

BASE_URL = CFG["base_url"].rstrip("/")
CATS = CFG["categories"]


# ---------------------------------------------------------------- utilities
def render(template: str, **ctx) -> str:
    """{{ var }} 치환 방식의 미니 템플릿 렌더러."""
    def repl(m):
        key = m.group(1).strip()
        return str(ctx.get(key, ""))
    return re.sub(r"\{\{\s*([\w_]+)\s*\}\}", repl, template)


def load_template(name: str) -> str:
    return (ROOT / "templates" / name).read_text(encoding="utf-8")


def parse_md_file(path: Path):
    """frontmatter + 본문 파싱."""
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.DOTALL)
    if not m:
        raise ValueError(f"frontmatter가 없습니다: {path}")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"')
    body = m.group(2).strip()
    html = markdown.markdown(body, extensions=MD_EXTENSIONS)
    # 글자 수 기반 예상 읽기 시간 (한국어 분당 500자 기준)
    chars = len(re.sub(r"\s", "", body))
    meta["reading_min"] = max(1, round(chars / 500))
    meta["chars"] = chars
    return meta, html, body


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def fmt_date(iso: str) -> str:
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d.year}년 {d.month}월 {d.day}일"


def adsense_head() -> str:
    client = CFG.get("adsense_client", "")
    if not client:
        return "<!-- AdSense: config.json 의 adsense_client 에 ca-pub-XXXX 를 넣으면 자동 삽입됩니다 -->"
    return (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/'
            f'adsbygoogle.js?client={client}" crossorigin="anonymous"></script>')


def ad_slot(label: str) -> str:
    """본문 광고 자리. 승인 후 자동광고를 쓰면 이 자리 없이도 광고가 붙지만,
    수동 단위를 쓰고 싶을 때를 위해 마크업 자리를 남겨 둔다."""
    client = CFG.get("adsense_client", "")
    if not client:
        return f"<!-- ad-slot: {label} -->"
    return (f'<div class="ad-box" aria-label="광고">'
            f'<ins class="adsbygoogle" style="display:block" data-ad-client="{client}" '
            f'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            f'<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>')


# ---------------------------------------------------------------- rendering
BASE = None  # lazy


def page_shell(*, title, description, url_path, content, og_type="website",
               json_ld="", noindex=False):
    global BASE
    if BASE is None:
        BASE = load_template("base.html")
    canonical = f"{BASE_URL}{url_path}"
    nav_links = "".join(
        f'<a href="{BASE_URL}/{slug}/" class="nav-cat">{c["emoji"]} {c["name"]}</a>'
        for slug, c in CATS.items())
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return render(
        BASE,
        lang="ko",
        site_name=CFG["site_name"],
        tagline=CFG["tagline"],
        title=esc(title),
        description=esc(description),
        canonical=canonical,
        base_url=BASE_URL,
        og_type=og_type,
        adsense_head=adsense_head(),
        robots_meta=robots,
        nav_links=nav_links,
        json_ld=json_ld,
        content=content,
        year=str(datetime.now(KST).year),
    )


def post_card(p) -> str:
    c = CATS[p["category"]]
    return f'''<article class="card">
  <a href="{p['url']}" class="card-link">
    <div class="card-cat" style="--cat-color:{c['color']}">{c['emoji']} {c['name']}</div>
    <h3 class="card-title">{esc(p['title'])}</h3>
    <p class="card-desc">{esc(p['description'])}</p>
    <div class="card-meta"><time datetime="{p['date']}">{fmt_date(p['date'])}</time> · {p['reading_min']}분 읽기</div>
  </a>
</article>'''


def build_post(p, posts):
    c = CATS[p["category"]]
    tags_html = "".join(f'<span class="tag">#{esc(t)}</span>'
                        for t in p.get("tags_list", []))
    related = [q for q in posts
               if q["category"] == p["category"] and q["url"] != p["url"]][:3]
    related_html = ""
    if related:
        cards = "".join(post_card(q) for q in related)
        related_html = f'<section class="related"><h2>이런 글은 어떠세요?</h2><div class="grid">{cards}</div></section>'

    # 첫 번째 H2 앞에 광고 슬롯 삽입
    body_html = p["html"]
    parts = body_html.split("<h2", 1)
    if len(parts) == 2:
        body_html = parts[0] + ad_slot("in-article-top") + "<h2" + parts[1]

    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": p["title"],
        "description": p["description"],
        "datePublished": p["date"],
        "dateModified": p["date"],
        "author": {"@type": "Person", "name": CFG["author"]},
        "publisher": {"@type": "Organization", "name": CFG["site_name"]},
        "mainEntityOfPage": f"{BASE_URL}{p['url_path']}",
        "inLanguage": "ko",
    }, ensure_ascii=False)

    content = render(
        load_template("post.html"),
        cat_url=f"{BASE_URL}/{p['category']}/",
        cat_color=c["color"],
        cat_label=f"{c['emoji']} {c['name']}",
        title=esc(p["title"]),
        date_iso=p["date"],
        date_human=fmt_date(p["date"]),
        reading_min=p["reading_min"],
        body=body_html,
        ad_bottom=ad_slot("below-article"),
        tags=tags_html,
        related=related_html,
    )
    out = OUT / p["category"] / p["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page_shell(
        title=f"{p['title']} | {CFG['site_name']}",
        description=p["description"],
        url_path=p["url_path"],
        content=content,
        og_type="article",
        json_ld=f'<script type="application/ld+json">{json_ld}</script>',
    ), encoding="utf-8")


def build_category(slug, posts):
    c = CATS[slug]
    mine = [p for p in posts if p["category"] == slug]
    cards = "".join(post_card(p) for p in mine) or "<p class='empty'>아직 글이 없습니다. 곧 채워질 예정입니다.</p>"
    content = f'''<header class="page-head" style="--cat-color:{c['color']}">
  <h1>{c['emoji']} {c['name']}</h1><p>{c['desc']}</p></header>
<div class="grid">{cards}</div>'''
    out = OUT / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page_shell(
        title=f"{c['name']} | {CFG['site_name']}",
        description=c["desc"],
        url_path=f"/{slug}/",
        content=content,
    ), encoding="utf-8")


def build_index(posts):
    latest = "".join(post_card(p) for p in posts[:9])
    cat_chips = "".join(
        f'<a class="chip" href="{BASE_URL}/{slug}/" style="--cat-color:{c["color"]}">{c["emoji"]} {c["name"]}</a>'
        for slug, c in CATS.items())
    content = render(
        load_template("index.html"),
        site_name=CFG["site_name"],
        tagline=CFG["tagline"],
        cat_chips=cat_chips,
        latest_cards=latest,
    )
    (OUT / "index.html").write_text(page_shell(
        title=f"{CFG['site_name']} - {CFG['tagline']}",
        description=CFG["description"],
        url_path="/",
        content=content,
    ), encoding="utf-8")


def build_static_pages():
    for md_file in sorted((ROOT / "pages").glob("*.md")):
        meta, html, _ = parse_md_file(md_file)
        slug = md_file.stem
        content = f'<article class="post static-page"><h1>{esc(meta["title"])}</h1><div class="post-body">{html}</div></article>'
        out = OUT / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page_shell(
            title=f"{meta['title']} | {CFG['site_name']}",
            description=meta.get("description", meta["title"]),
            url_path=f"/{slug}/",
            content=content,
        ), encoding="utf-8")


def build_feeds_and_seo(posts):
    now = datetime.now(KST)
    # sitemap
    urls = [f"{BASE_URL}/"] + [f"{BASE_URL}/{s}/" for s in CATS] + \
           [f"{BASE_URL}{p['url_path']}" for p in posts] + \
           [f"{BASE_URL}/{s.stem}/" for s in (ROOT / "pages").glob("*.md")]
    items = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{now.strftime('%Y-%m-%d')}</lastmod></url>"
        for u in urls)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>\n',
        encoding="utf-8")

    # RSS
    rss_items = ""
    for p in posts[:20]:
        pub = datetime.strptime(p["date"], "%Y-%m-%d").replace(tzinfo=KST)
        rss_items += f'''  <item>
    <title>{esc(p['title'])}</title>
    <link>{BASE_URL}{p['url_path']}</link>
    <guid>{BASE_URL}{p['url_path']}</guid>
    <pubDate>{pub.strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>
    <description>{esc(p['description'])}</description>
  </item>\n'''
    (OUT / "rss.xml").write_text(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>{esc(CFG['site_name'])}</title>
  <link>{BASE_URL}/</link>
  <description>{esc(CFG['description'])}</description>
  <language>ko</language>
{rss_items}</channel></rss>\n''', encoding="utf-8")

    # robots.txt / ads.txt
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    ads_src = ROOT / "ads.txt"
    if ads_src.exists():
        shutil.copy(ads_src, OUT / "ads.txt")

    # 404
    content = ('<div class="page-head"><h1>페이지를 찾을 수 없습니다</h1>'
               f'<p>주소가 바뀌었거나 삭제된 페이지입니다. <a href="{BASE_URL}/">홈으로 돌아가기</a></p></div>')
    (OUT / "404.html").write_text(page_shell(
        title=f"404 | {CFG['site_name']}", description="페이지를 찾을 수 없습니다",
        url_path="/404.html", content=content, noindex=True), encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "static", OUT / "static")

    posts = []
    for cat in CATS:
        for md_file in sorted((ROOT / "content" / cat).glob("*.md")):
            meta, html, _body = parse_md_file(md_file)
            slug = md_file.stem
            tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
            posts.append({
                **meta,
                "category": cat,
                "slug": slug,
                "html": html,
                "tags_list": tags,
                "url_path": f"/{cat}/{slug}/",
                "url": f"{BASE_URL}/{cat}/{slug}/",
            })
    posts.sort(key=lambda p: p["date"], reverse=True)

    for p in posts:
        build_post(p, posts)
    for slug in CATS:
        build_category(slug, posts)
    build_index(posts)
    build_static_pages()
    build_feeds_and_seo(posts)

    print(f"✅ 빌드 완료: 글 {len(posts)}편 → {OUT}")
    for p in posts:
        print(f"   - [{CATS[p['category']]['name']}] {p['title']} ({p['chars']:,}자)")

    if "--serve" in sys.argv:
        import http.server, functools, os
        os.chdir(OUT)
        http.server.test(
            HandlerClass=functools.partial(http.server.SimpleHTTPRequestHandler),
            port=8000)


if __name__ == "__main__":
    main()
