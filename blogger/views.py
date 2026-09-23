import html
import re
from datetime import date

from bs4 import BeautifulSoup, Comment, Tag
from django.http import HttpResponse
from django.shortcuts import render

DEFAULT_EYEBROW = "EverClif Insights"
DEFAULT_AUTHOR = "EverClif Team"
# One-time setup: upload the founder/brand photo to the WordPress media
# library once, then paste its URL here. Every generated post will use it
# automatically — no need to re-enter it per upload. Can still be
# overridden per-post via the "CTA image URL" advanced field.
DEFAULT_CTA_IMAGE = "https://everclif.com/insights/wp-content/uploads/2026/07/founder.webp"
DEFAULT_CTA_TEXT = (
    "Want a strategy built around your audience and goals? "
    "I can help you plan and execute it."
)
DEFAULT_CTA_LINK = "https://calendly.com/anirban-everclif/30min"
DEFAULT_CTA_BUTTON_TEXT = "Talk to Us"
WORDS_PER_MINUTE = 200

FAQ_HEADING_RE = re.compile(r'\bfaqs?\b|\bfrequently asked questions\b', re.I)

EVERCLIF_CSS = """
:root {
    --primary: #000080;
    --accent: #1E90FF;
    --white: #ffffff;
    --light: #F5F6F7;
    --dark: #333333;
    --amber: #F59E0B;
    --amber-dark: #D97706;
    --amber-soft: rgba(245, 158, 11, 0.12);
}

.ec-blog-post {
    font-family: 'Satoshi', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    color: var(--dark);
    line-height: 1.6;
    font-variation-settings: 'wght' 400;
}

/* Satoshi is a variable font, and font-variation-settings is inherited --
   the base 'wght' 400 above silently overrides `font-weight` on any bold
   descendant that doesn't also set its own 'wght' (a well-known variable-font
   gotcha). strong/b need a blanket rule here since they can appear anywhere
   -- listicle lead-ins, table cells, FAQ answers -- not just in a few fixed
   selectors. Every other bold selector in this file sets its matching
   font-variation-settings alongside font-weight for the same reason. */
.ec-blog-post strong,
.ec-blog-post b {
    font-weight: 700;
    font-variation-settings: 'wght' 700;
}

.ec-blog-post .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
}

.ec-blog-post .blog-hero {
    position: relative;
    padding: 150px 0 70px;
    overflow: hidden;
    background: linear-gradient(135deg, var(--primary) 0%, #14207A 50%, #0E2E8F 100%);
}

.ec-blog-post .blog-hero-inner {
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
    gap: 48px;
    align-items: center;
}

.ec-blog-post .blog-hero-text {
    position: relative;
    z-index: 1;
}

.ec-blog-post .blog-hero-media {
    width: 100%;
}

.ec-blog-post .blog-hero-img {
    width: 100%;
    aspect-ratio: 5 / 3;
    object-fit: cover;
    display: block;
    border-radius: 16px;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
}

.ec-blog-post .blog-hero-eyebrow {
    display: inline-block;
    font-size: 13px;
    font-weight: 700;
    font-variation-settings: 'wght' 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: var(--white);
    background: rgba(245, 158, 11, 0.22);
    border: 1px solid rgba(245, 158, 11, 0.55);
    padding: 6px 14px;
    border-radius: 99px;
    margin-bottom: 20px;
}

.ec-blog-post .blog-hero-title {
    font-size: 40px;
    font-weight: 700;
    font-variation-settings: 'wght' 700;
    color: var(--white);
    line-height: 1.25;
    margin-bottom: 16px;
}

.ec-blog-post .blog-hero-meta {
    font-size: 15px;
    color: rgba(255, 255, 255, 0.75);
}

.ec-blog-post .blog-body {
    padding: 64px 0 40px;
    background: var(--white);
}

.ec-blog-post .blog-layout {
    display: grid;
    grid-template-columns: 260px minmax(0, 1fr);
    gap: 64px;
    align-items: start;
}

.ec-blog-post .blog-toc {
    position: sticky;
    top: 100px;
    align-self: start;
    max-height: calc(100vh - 130px);
    overflow-y: auto;
}

.ec-blog-post .blog-toc-label {
    font-size: 12px;
    font-weight: 700;
    font-variation-settings: 'wght' 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 14px;
}

.ec-blog-post .blog-toc-list {
    list-style: none;
    border-left: 2px solid rgba(30, 144, 255, 0.18);
}

.ec-blog-post .toc-link {
    display: block;
    padding: 7px 0 7px 16px;
    margin-left: -2px;
    border-left: 2px solid transparent;
    font-size: 14.5px;
    color: var(--dark);
    text-decoration: none;
    line-height: 1.4;
    transition: color 0.2s ease, border-color 0.2s ease;
}

.ec-blog-post .toc-link--sub {
    padding-left: 30px;
    font-size: 13.5px;
    opacity: 0.85;
}

.ec-blog-post .toc-link:hover {
    color: var(--primary);
}

.ec-blog-post .toc-link.is-active {
    color: var(--primary);
    font-weight: 700;
    font-variation-settings: 'wght' 700;
    border-left-color: var(--amber);
}

.ec-blog-post .blog-content {
    max-width: 720px;
    font-size: 17px;
    line-height: 1.8;
    color: var(--dark);
}

.ec-blog-post .blog-content > p {
    margin-bottom: 22px;
}

.ec-blog-post .blog-content h2 {
    font-size: 30px;
    font-weight: 700;
    font-variation-settings: 'wght' 700;
    color: var(--primary);
    margin: 52px 0 18px;
    line-height: 1.3;
}

.ec-blog-post .blog-content h2:first-of-type {
    margin-top: 36px;
}

.ec-blog-post .blog-content h3 {
    font-size: 22px;
    font-weight: 700;
    font-variation-settings: 'wght' 700;
    color: var(--primary);
    margin: 38px 0 14px;
    line-height: 1.35;
}

.ec-blog-post .blog-content h4 {
    font-size: 18px;
    font-weight: 700;
    font-variation-settings: 'wght' 700;
    color: var(--accent);
    margin: 28px 0 10px;
}

.ec-blog-post .blog-content em {
    color: var(--primary);
    font-style: italic;
}

.ec-blog-post .blog-content img {
    max-width: 100%;
    height: auto;
    border-radius: 10px;
    display: block;
    margin: 8px 0 24px;
}

.ec-blog-post .blog-content ul,
.ec-blog-post .blog-content ol {
    margin: 0 0 24px;
    padding-left: 22px;
}

.ec-blog-post .blog-content li {
    margin-bottom: 12px;
}

.ec-blog-post .blog-content li:last-child {
    margin-bottom: 0;
}

.ec-blog-post .blog-content li > ul,
.ec-blog-post .blog-content li > ol {
    margin-top: 10px;
    margin-bottom: 0;
}

.ec-blog-post .blog-content .table-wrap {
    overflow-x: auto;
    margin: 8px 0 28px;
    border: 1px solid rgba(30, 144, 255, 0.18);
    border-radius: 12px;
}

.ec-blog-post .blog-content table {
    width: 100%;
    border-collapse: collapse;
    font-size: 15.5px;
}

.ec-blog-post .blog-content th,
.ec-blog-post .blog-content td {
    padding: 14px 18px;
    text-align: left;
    border-bottom: 1px solid rgba(30, 144, 255, 0.14);
}

.ec-blog-post .blog-content thead th {
    background: var(--primary);
    color: var(--white);
    font-weight: 700;
    font-variation-settings: 'wght' 700;
    font-size: 13px;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    white-space: nowrap;
}

.ec-blog-post .blog-content tbody tr:nth-child(even) {
    background: var(--light);
}

.ec-blog-post .blog-content tbody tr:last-child td {
    border-bottom: none;
}

.ec-blog-post .blog-closing-line {
    font-size: 19px;
    font-weight: 600;
    font-variation-settings: 'wght' 600;
    font-style: italic;
    color: var(--primary);
}

.ec-blog-post .blog-cta-banner {
    display: flex;
    align-items: center;
    gap: 28px;
    background: linear-gradient(135deg, var(--primary) 0%, #14207A 50%, #0E2E8F 100%);
    border-radius: 16px;
    padding: 32px;
    margin: 44px 0 48px;
    box-shadow: 0 10px 30px rgba(0, 0, 128, 0.22);
}

.ec-blog-post .blog-cta-img {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--amber);
    flex-shrink: 0;
}

.ec-blog-post .blog-cta-body {
    flex: 1;
}

.ec-blog-post .blog-cta-text {
    color: var(--white);
    font-size: 17px;
    line-height: 1.6;
    margin-bottom: 16px;
}

.ec-blog-post .blog-cta-btn {
    display: inline-block;
    padding: 11px 26px;
    font-size: 16px;
    font-weight: 700;
    font-variation-settings: 'wght' 700;
    color: var(--primary);
    background: linear-gradient(135deg, #FBBF45 0%, var(--amber) 100%);
    border: 2px solid var(--amber);
    border-radius: 6px;
    text-decoration: none;
    box-shadow: 0 6px 22px rgba(245, 158, 11, 0.4);
    transition: all 0.3s ease;
}

.ec-blog-post .blog-cta-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(245, 158, 11, 0.55);
}

.ec-blog-post .blog-faq {
    background: var(--light);
    padding: 80px 0;
}

.ec-blog-post .blog-faq-container {
    max-width: 800px;
}

.ec-blog-post .blog-faq-title {
    font-size: 34px;
    font-weight: 700;
    font-variation-settings: 'wght' 700;
    color: var(--primary);
    text-align: center;
    margin-bottom: 40px;
}

.ec-blog-post .blog-faq-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.ec-blog-post .blog-faq-item {
    background: var(--white);
    border: 1px solid rgba(30, 144, 255, 0.18);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(30, 144, 255, 0.06);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.ec-blog-post .blog-faq-item.is-open {
    border-color: var(--amber);
    box-shadow: 0 6px 18px rgba(245, 158, 11, 0.18);
}

.ec-blog-post .blog-faq-question {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    background: none;
    border: none;
    cursor: pointer;
    text-align: left;
    padding: 20px 24px;
    font-size: 16px;
    font-weight: 600;
    font-variation-settings: 'wght' 600;
    color: var(--primary);
    font-family: inherit;
}

.ec-blog-post .blog-faq-toggle {
    flex-shrink: 0;
    width: 26px;
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--amber-soft);
    color: var(--amber-dark);
    font-size: 18px;
    font-weight: 700;
    font-variation-settings: 'wght' 700;
    transition: transform 0.25s ease;
}

.ec-blog-post .blog-faq-item.is-open .blog-faq-toggle {
    transform: rotate(45deg);
}

.ec-blog-post .blog-faq-answer {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.ec-blog-post .blog-faq-item.is-open .blog-faq-answer {
    max-height: 600px;
}

.ec-blog-post .blog-faq-answer p {
    padding: 0 24px 22px;
    color: var(--dark);
    font-size: 15.5px;
    line-height: 1.7;
}

@media (max-width: 900px) {
    .ec-blog-post .blog-layout {
        grid-template-columns: 1fr;
        gap: 32px;
    }

    .ec-blog-post .blog-toc {
        position: static;
        max-height: none;
        order: -1;
        border: 1px solid rgba(30, 144, 255, 0.18);
        border-radius: 12px;
        padding: 18px 20px;
    }

    .ec-blog-post .blog-toc-list {
        max-height: 220px;
        overflow-y: auto;
    }

    .ec-blog-post .blog-hero-inner {
        grid-template-columns: 1fr;
        gap: 32px;
    }

    .ec-blog-post .blog-hero-media {
        max-width: 480px;
        margin: 0 auto;
    }

    .ec-blog-post .blog-hero-title {
        font-size: 32px;
    }
}

@media (max-width: 600px) {
    .ec-blog-post .blog-hero {
        padding: 140px 0 48px;
    }

    .ec-blog-post .blog-cta-banner {
        flex-direction: column;
        text-align: center;
    }

    .ec-blog-post .blog-faq-title {
        font-size: 26px;
    }
}
"""

FAQ_TOGGLE_JS = """
document.querySelectorAll('.blog-faq-item').forEach(function (item) {
    var question = item.querySelector('.blog-faq-question');
    if (!question) return;
    question.addEventListener('click', function () {
        item.classList.toggle('is-open');
    });
});
"""


def _slugify(text, used):
    slug = re.sub(r'[^a-z0-9]+', '-', text.strip().lower()).strip('-') or 'section'
    base, n = slug, 2
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    used.add(slug)
    return slug


def _extract_title(soup):
    h1 = soup.find('h1')
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)
    if soup.title and soup.title.get_text(strip=True):
        return soup.title.get_text(strip=True)
    return 'Untitled Post'


def _extract_feature_image(soup):
    og = soup.find('meta', attrs={'property': 'og:image'})
    if og and og.get('content'):
        return og['content']
    for keyword in ('feature', 'featured', 'hero', 'thumbnail'):
        img = soup.find('img', class_=lambda c: c and keyword in c.lower())
        if img and img.get('src'):
            return img['src']
    img = soup.find('img')
    if img and img.get('src'):
        return img['src']
    return None


def _extract_eyebrow(soup):
    """Pull the hero eyebrow/category label (e.g. 'Technical SEO') out of the doc, if present."""
    tag = soup.find(class_=lambda c: c and 'eyebrow' in c.lower())
    if tag and tag.get_text(strip=True):
        text = tag.get_text(strip=True)
        tag.extract()
        return text
    return None


def _extract_author_date(soup):
    """Pull 'Author · Date · N min read' style bylines out of the doc, if present."""
    meta_author = soup.find('meta', attrs={'name': 'author'})
    author = meta_author['content'].strip() if meta_author and meta_author.get('content') else None

    byline = soup.find(class_=lambda c: c and any(
        k in c.lower() for k in ('byline', 'author', 'post-meta', 'entry-meta', 'hero-meta')
    ))
    date_str = None
    if byline:
        text = byline.get_text(' ', strip=True)
        parts = [p.strip() for p in re.split(r'[·|•]', text) if p.strip()]
        if not author and parts:
            author = parts[0]
        for p in parts[1:]:
            if re.search(r'\d{4}', p) and not re.search(r'read', p, re.I):
                date_str = p
        byline.extract()
    return author, date_str


def _wrap_answer(answer_html):
    answer_html = answer_html.strip()
    if not answer_html:
        return ''
    if BeautifulSoup(answer_html, 'html.parser').find('p'):
        return answer_html
    return f'<p>{answer_html}</p>'


def _extract_prebuilt_faq(soup):
    """Handle FAQ content that already uses this template's own markup
    (a <section class="blog-faq"> full of .blog-faq-item blocks) -- e.g. when
    re-processing a file that was already built by this tool. This section
    is typically a sibling of the article, not nested inside it, so we search
    the whole document rather than just the content root."""
    section = soup.find(class_='blog-faq')
    if not section:
        return []
    pairs = []
    for item in section.find_all(class_='blog-faq-item'):
        q_el = item.find(class_='blog-faq-question')
        a_el = item.find(class_='blog-faq-answer')
        if not q_el or not a_el:
            continue
        toggle = q_el.find(class_='blog-faq-toggle')
        toggle_text = toggle.get_text(strip=True) if toggle else ''
        if toggle:
            toggle.extract()
        question = q_el.get_text(strip=True)
        if toggle_text and question.endswith(toggle_text):
            question = question[:-len(toggle_text)].strip()
        answer_html = ''.join(str(c) for c in a_el.contents)
        pairs.append((question, _wrap_answer(answer_html)))
    if pairs:
        section.extract()
    return pairs


def _extract_faq(root):
    """Find an FAQ section (dl, details, or heading + Q/A blocks) and remove it from the tree."""
    pairs = []

    for dl in list(root.find_all('dl')):
        for dt, dd in zip(dl.find_all('dt'), dl.find_all('dd')):
            pairs.append((dt.get_text(strip=True), ''.join(str(c) for c in dd.contents)))
        dl.extract()

    for details in list(root.find_all('details')):
        summary = details.find('summary')
        if summary:
            question = summary.get_text(strip=True)
            summary.extract()
            pairs.append((question, ''.join(str(c) for c in details.contents)))
        details.extract()

    children = list(root.find_all(recursive=False))
    n = len(children)
    consumed = []
    i = 0
    while i < n:
        node = children[i]
        if isinstance(node, Tag) and node.name in ('h2', 'h3', 'h4') and FAQ_HEADING_RE.search(node.get_text(strip=True)):
            consumed.append(node)
            j = i + 1
            cur_q, cur_a = None, []
            while j < n:
                nxt = children[j]
                if isinstance(nxt, Tag) and nxt.name == 'h2':
                    break
                if isinstance(nxt, Tag) and nxt.name in ('h3', 'h4'):
                    if cur_q is not None:
                        pairs.append((cur_q, ''.join(cur_a)))
                    cur_q = nxt.get_text(strip=True)
                    cur_a = []
                elif cur_q is not None and isinstance(nxt, Tag):
                    cur_a.append(str(nxt))
                consumed.append(nxt)
                j += 1
            if cur_q is not None:
                pairs.append((cur_q, ''.join(cur_a)))
            i = j
        else:
            i += 1

    for node in consumed:
        node.extract()

    return [(q, _wrap_answer(a)) for q, a in pairs if q]


def _build_toc(root):
    """Build the TOC from top-level h2/h3 headings only (`recursive=False`).

    Restricting to direct children of `root` -- rather than all h2/h3 anywhere
    in the content -- is what keeps this safe: a real subsection heading (e.g.
    a "How Pricing Works" h3 inside a listicle, sitting alongside its sibling
    h2s) gets picked up, while a decorative h3 used as a title inside a nested
    callout/stat-box/comparison-table caption does not, since it isn't a direct
    child. An earlier version limited this to h2 only, which was blunter than
    necessary and dropped legitimate h3 sub-items from listicle/comparison
    posts -- this recovers those without reintroducing the noise.
    """
    used_ids = set(filter(None, (t.get('id') for t in root.find_all(True))))
    toc_items = []
    for heading in root.find_all(['h2', 'h3'], recursive=False):
        text = heading.get_text(strip=True)
        if not text:
            continue
        if not heading.get('id'):
            heading['id'] = _slugify(text, used_ids)
        toc_items.append((heading['id'], text, heading.name[1]))
    return toc_items


def _extract_cta(root):
    """Pull an existing CTA banner's text/link/image/button-label out of the source,
    if present, and remove it so we don't end up with two (the source one plus our
    injected one)."""
    tag = root.find(class_=lambda c: c and 'cta-banner' in c.lower())
    if not tag:
        return None, None, None, None
    text_el = tag.find(class_=lambda c: c and 'cta-text' in c.lower())
    text = text_el.get_text(strip=True) if text_el else None
    link_el = tag.find(class_=lambda c: c and 'cta-btn' in c.lower()) or tag.find('a', href=True)
    link = link_el['href'].strip() if link_el and link_el.get('href') else None
    button_text = link_el.get_text(strip=True) if link_el else None
    img_el = tag.find('img', src=True)
    image = img_el['src'].strip() if img_el else None
    tag.extract()
    return text, link, image, button_text


def _format_today():
    d = date.today()
    return f"{d.day} {d.strftime('%B')} {d.year}"


def _split_for_cta(root):
    """Split root's content into two halves so the CTA banner can be inserted
    ~35% of the way down the article.

    The split point is snapped to fall immediately before a top-level h2 --
    i.e. a real section boundary -- rather than at a raw tag-count fraction.
    A raw fraction can land mid-section: between a lead-in paragraph and the
    list/table it introduces, or inside a listicle's <ol> or a comparison
    <table>, breaking the content apart. Restricting candidates to h2
    boundaries (and excluding the very first one, so the CTA never sits above
    the intro) guarantees the banner only ever lands between whole sections.
    If the article has no such boundary (e.g. a single-section post), the CTA
    is appended at the end instead of guessing a mid-content split.
    """
    children = list(root.contents)
    tag_indices = [i for i, c in enumerate(children) if isinstance(c, Tag)]
    h2_indices = [i for i in tag_indices if children[i].name == 'h2']
    candidates = h2_indices[1:]

    if not candidates:
        split_idx = len(children)
    else:
        target_pos = round(len(tag_indices) * 0.35)
        target_idx = tag_indices[min(target_pos, len(tag_indices) - 1)]
        split_idx = min(candidates, key=lambda i: abs(i - target_idx))

    content_part_1 = ''.join(str(c) for c in children[:split_idx])
    content_part_2 = ''.join(str(c) for c in children[split_idx:])
    return content_part_1, content_part_2


def build_everclif_post(source_html, *, eyebrow=None, author=None, cta_text=None, cta_link=None, cta_image=None, cta_button_text=None, feature_image=None):
    soup = BeautifulSoup(source_html, 'html.parser')

    for tag in soup.find_all(['style', 'script']):
        tag.decompose()
    for tag in soup.find_all('link', rel=lambda r: r and 'stylesheet' in r):
        tag.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    title = _extract_title(soup)
    h1 = soup.find('h1')
    if h1:
        h1.extract()

    extracted_feature_image = _extract_feature_image(soup)
    feature_image = (feature_image or extracted_feature_image or '').strip() or None

    root = soup.find('article') or soup.find('main') or soup.find('body') or soup

    if extracted_feature_image:
        first_img = root.find('img')
        if first_img is not None and first_img.get('src') == extracted_feature_image:
            first_img.extract()

    # Author/date/eyebrow live in the hero header, which sits outside `root`
    # (root is the inner <article>/<main> content), so search the whole doc.
    detected_eyebrow = _extract_eyebrow(soup)
    detected_author, detected_date = _extract_author_date(soup)
    author = (author or detected_author or DEFAULT_AUTHOR).strip()
    date_str = detected_date or _format_today()
    eyebrow = (eyebrow or detected_eyebrow or DEFAULT_EYEBROW).strip()

    # A source file may already contain a CTA banner (e.g. it was exported from
    # this same template before); reuse its content and remove it from the body
    # so we don't inject a second, generic one on top of it.
    detected_cta_text, detected_cta_link, detected_cta_image, detected_cta_button = _extract_cta(root)
    cta_text = (cta_text or detected_cta_text or DEFAULT_CTA_TEXT).strip()
    cta_link = (cta_link or detected_cta_link or DEFAULT_CTA_LINK).strip()
    cta_image = (cta_image or detected_cta_image or DEFAULT_CTA_IMAGE).strip()
    cta_button_text = (cta_button_text or detected_cta_button or DEFAULT_CTA_BUTTON_TEXT).strip()
    faq_pairs = _extract_prebuilt_faq(soup) or _extract_faq(root)
    toc_items = _build_toc(root)
    if faq_pairs:
        toc_items.append(('faq', 'FAQ', '2'))

    # Wrap every comparison table in a scrollable container so wide tables
    # (e.g. a "10 agencies compared" table) don't overflow the 720px content
    # column on mobile, and so they pick up the .table-wrap card styling.
    for table in root.find_all('table'):
        wrapper = soup.new_tag('div', attrs={'class': 'table-wrap'})
        table.wrap(wrapper)

    word_count = len(root.get_text(' ', strip=True).split())
    read_minutes = max(1, round(word_count / WORDS_PER_MINUTE))

    content_part_1, content_part_2 = _split_for_cta(root)

    toc_html = '\n'.join(
        f'<li><a href="#{id_}" class="toc-link{" toc-link--sub" if level == "3" else ""}" '
        f'data-toc-level="{level}">{html.escape(text)}</a></li>'
        for id_, text, level in toc_items
    )

    if feature_image:
        hero_media = f'<img src="{html.escape(feature_image, quote=True)}" alt="{html.escape(title)}" class="blog-hero-img">'
    else:
        hero_media = (
            "<!-- No featured image found in the uploaded HTML. "
            "Replace with the WordPress Featured Image, e.g. "
            "<?php the_post_thumbnail('large', ['class' => 'blog-hero-img']); ?> -->"
        )

    if faq_pairs:
        faq_items_html = ''.join(
            f'''
        <div class="blog-faq-item">
          <button type="button" class="blog-faq-question">
            <span>{html.escape(q)}</span>
            <span class="blog-faq-toggle">+</span>
          </button>
          <div class="blog-faq-answer">{a}</div>
        </div>'''
            for q, a in faq_pairs
        )
        faq_section = f'''
        <section class="blog-faq">
            <div class="container blog-faq-container">
                <h2 class="blog-faq-title" id="faq">FAQ</h2>
                <div class="blog-faq-list">{faq_items_html}
                </div>
            </div>
        </section>'''
        faq_script = f'<script>{FAQ_TOGGLE_JS}</script>'
    else:
        faq_section = ''
        faq_script = ''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<style>{EVERCLIF_CSS}</style>
</head>
<body>
<div class="ec-blog-post">
    <header class="blog-hero">
        <div class="container blog-hero-inner">
            <div class="blog-hero-text">
                <span class="blog-hero-eyebrow">{html.escape(eyebrow)}</span>
                <h1 class="blog-hero-title">{html.escape(title)}</h1>
                <p class="blog-hero-meta">{html.escape(author)} &middot; {html.escape(date_str)} &middot; {read_minutes} min read</p>
            </div>
            <div class="blog-hero-media">
                {hero_media}
            </div>
        </div>
    </header>

    <section class="blog-body">
        <div class="container blog-layout">
            <aside class="blog-toc">
                <p class="blog-toc-label">On this page</p>
                <nav aria-label="Table of contents">
                    <ul class="blog-toc-list">
                        {toc_html}
                    </ul>
                </nav>
            </aside>

            <article class="blog-content">
                {content_part_1}
                <aside class="blog-cta-banner">
                    <img src="{html.escape(cta_image, quote=True)}" alt="{html.escape(author)}" class="blog-cta-img" width="120" height="120">
                    <div class="blog-cta-body">
                        <p class="blog-cta-text">{html.escape(cta_text)}</p>
                        <a href="{html.escape(cta_link, quote=True)}" class="blog-cta-btn" target="_blank" rel="noopener noreferrer">{html.escape(cta_button_text)}</a>
                    </div>
                </aside>
                {content_part_2}
            </article>
        </div>
    </section>
    {faq_section}
</div>
{faq_script}
</body>
</html>
'''


def index(request):
    if request.method == 'GET':
        return render(request, 'index.html')

    html_file = request.FILES.get('html_file')
    if not html_file:
        return render(request, 'index.html', {'errors': ['Please upload an HTML file.']})

    eyebrow = request.POST.get('eyebrow', '').strip()
    author = request.POST.get('author', '').strip()
    cta_text = request.POST.get('cta_text', '').strip()
    cta_link = request.POST.get('cta_link', '').strip()
    cta_image = request.POST.get('cta_image', '').strip()
    cta_button_text = request.POST.get('cta_button_text', '').strip()
    feature_image = request.POST.get('feature_image', '').strip()

    source_html = html_file.read().decode('utf-8', errors='replace')

    try:
        output_html = build_everclif_post(
            source_html,
            eyebrow=eyebrow or None,
            author=author or None,
            cta_text=cta_text or None,
            cta_link=cta_link or None,
            cta_image=cta_image or None,
            cta_button_text=cta_button_text or None,
            feature_image=feature_image or None,
        )
    except Exception as exc:
        return render(request, 'index.html', {'errors': [f'Could not convert this file: {exc}']})

    out_filename = html_file.name.rsplit('.', 1)[0] + '_everclif.html'
    response = HttpResponse(output_html, content_type='text/html; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{out_filename}"'
    return response
