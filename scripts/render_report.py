#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法律检索报告渲染脚本（法律检索智能体 / C002 FR-06）

职责分工（重要）：
  - 真实法条/类案检索由「华宇元典」MCP 工具完成（yuandian_law_vector_search /
    yuandian_case_vector_search），由调用方（Agent）执行并把结果整理成 JSON；
  - 本脚本只负责把 JSON 渲染成结构化检索报告（.md + 可选 .docx），
    纯 Python 标准库、无外部依赖、离线可用、数据不出域。

用法：
  python render_report.py <input.json> <output_dir> [--docx]

输入 JSON 结构：
{
  "query": "自然语言检索问题",
  "laws": [
    {"fgtitle":"法规名称","num":"第X条","content":"法条内容","sxx":"现行有效",
     "effect1":"司法解释","effect2":"高法司法解释","start":20210101,
     "url":"官方链接","score":1.18}
  ],
  "cases": [
    {"title":"案件名","ah":"案号","jbdw":"法院","jaDate":20250618,
     "anyou":["案由"],"spcx":"二审案件","content":"案情/裁判要旨",
     "url":"官方链接","score":1.07}
  ]
}
"""
import json
import os
import re
import sys
import datetime
import zipfile

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
PKG_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
DOC_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def safe_filename(name):
    return re.sub(r'[\\/:*?"<>|\r\n\t ]+', '_', name)[:60]


def fmt_date(v):
    s = str(v or "").strip()
    if len(s) == 8 and s.isdigit():
        return "%s-%s-%s" % (s[0:4], s[4:6], s[6:8])
    return s or "—"


def clip(text, n=600):
    text = (text or "").replace("\n", " ").strip()
    return text if len(text) <= n else text[:n] + "……"


# ---------- Markdown 报告 ----------
def build_markdown(data):
    query = data.get("query", "").strip()
    laws = data.get("laws", []) or []
    cases = data.get("cases", []) or []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    L = []
    L.append("# 法律检索报告")
    L.append("")
    L.append("- **检索问题**：%s" % query)
    L.append("- **生成时间**：%s" % now)
    L.append("- **数据来源**：华宇元典法律数据（law_vector_search / case_vector_search）")
    L.append("- **命中**：法条 %d 条 · 类案 %d 篇" % (len(laws), len(cases)))
    L.append("")
    L.append("> 本报告由 AI 依据真实法律数据库检索生成，法条时效性以库内标注为准；"
             "**检索结论仅供承办律师参考，须经律师核对确认后方可用于正式法律意见或文书**。")
    L.append("")

    L.append("## 一、法条依据")
    if not laws:
        L.append("")
        L.append("*未命中法条，请调整检索问题或放宽过滤条件。*")
    for i, f in enumerate(laws, 1):
        L.append("")
        L.append("### %d. %s %s" % (i, f.get("fgtitle", "").strip(), f.get("num", "").strip()))
        meta = []
        if f.get("sxx"):
            meta.append("时效性：%s" % f["sxx"])
        if f.get("effect1"):
            meta.append("效力级别：%s" % f["effect1"])
        if f.get("effect2"):
            meta.append("类型：%s" % f["effect2"])
        if f.get("start"):
            meta.append("实施日期：%s" % fmt_date(f["start"]))
        if f.get("score") is not None:
            meta.append("相关度：%.3f" % float(f["score"]))
        if meta:
            L.append("- " + " ｜ ".join(meta))
        L.append("")
        L.append(clip(f.get("content", ""), 1200))
        if f.get("url"):
            L.append("")
            L.append("原文链接：%s" % f["url"])

    L.append("")
    L.append("## 二、相关类案")
    if not cases:
        L.append("")
        L.append("*未命中类案。*")
    for i, c in enumerate(cases, 1):
        L.append("")
        ay = c.get("anyou") or c.get("ay") or []
        ay = "、".join(ay) if isinstance(ay, list) else str(ay)
        L.append("### %d. %s" % (i, c.get("title", "").strip()))
        meta = []
        if c.get("ah"):
            meta.append("案号：%s" % c["ah"])
        if c.get("jbdw"):
            meta.append("法院：%s" % c["jbdw"])
        if c.get("spcx"):
            meta.append("审级：%s" % c["spcx"])
        if c.get("jaDate"):
            meta.append("结案：%s" % fmt_date(c["jaDate"]))
        if ay:
            meta.append("案由：%s" % ay)
        if c.get("score") is not None:
            meta.append("相似度：%.3f" % float(c["score"]))
        if meta:
            L.append("- " + " ｜ ".join(meta))
        L.append("")
        L.append("**裁判要旨/案情摘要**：" + clip(c.get("content", ""), 800))
        if c.get("url"):
            L.append("")
            L.append("案例链接：%s" % c["url"])

    L.append("")
    L.append("## 三、检索小结")
    L.append("")
    if laws:
        L.append("- 核心法条依据：%s" %
                 "；".join("%s%s" % (f.get("fgtitle", ""), f.get("num", "")) for f in laws[:3]))
    if cases:
        L.append("- 可参考类案：%s" %
                 "；".join("%s（%s）" % (c.get("title", "")[:20], c.get("ah", "")) for c in cases[:3]))
    L.append("- 使用提示：法条时效性、案例裁判尺度可能随修法/新规变化，"
             "引用前请通过原文链接复核最新有效版本。")
    L.append("")
    L.append("---")
    L.append("*本报告为 AI 检索初稿，不构成法律意见，须经承办律师终审确认。*")
    return "\n".join(L)


# ---------- 零依赖 .docx 生成（OpenXML） ----------
def xml_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def bold_runs(text):
    parts = re.split(r'(\*\*.+?\*\*)', text)
    out = []
    for p in parts:
        if len(p) >= 4 and p.startswith("**") and p.endswith("**"):
            out.append('<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r>'
                       % xml_escape(p[2:-2]))
        elif p:
            out.append('<w:r><w:t xml:space="preserve">%s</w:t></w:r>' % xml_escape(p))
    return "".join(out)


def md_paragraph(text, style=None):
    ppr = ('<w:pPr><w:pStyle w:val="%s"/></w:pPr>' % xml_escape(style)) if style else ""
    return "<w:p>%s%s</w:p>" % (ppr, bold_runs(text))


def md_to_docx_body(md_text):
    body = []
    for raw in md_text.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("### "):
            body.append(md_paragraph(line[4:], "Heading3"))
        elif line.startswith("## "):
            body.append(md_paragraph(line[3:], "Heading2"))
        elif line.startswith("# "):
            body.append(md_paragraph(line[2:], "Heading1"))
        elif line.startswith("> "):
            body.append(md_paragraph(line[2:], "Quote"))
        elif line.startswith("- ") or line.startswith("* "):
            body.append(md_paragraph(line[2:], "ListBullet"))
        elif line.strip() == "---":
            continue
        else:
            body.append(md_paragraph(line, None))
    sect = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1440" w:bottom="1440" w:left="1440" w:right="1440"/></w:sectPr>')
    return "".join(body) + sect


def build_docx(md_text, out_path):
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="%s"><w:body>%s</w:body></w:document>'
        % (W_NS, md_to_docx_body(md_text))
    )
    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="%s">'
        '<w:docDefaults><w:rPrDefault><w:rPr>'
        '<w:rFonts w:ascii="Calibri" w:eastAsia="\u5b8b\u4f53" w:hAnsi="Calibri" w:cs="Times New Roman"/>'
        '<w:sz w:val="21"/></w:rPr></w:rPrDefault></w:docDefaults>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>'
        '<w:pPr><w:keepNext/><w:spacing w:before="240" w:after="60"/><w:outlineLvl w:val="0"/></w:pPr>'
        '<w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>'
        '<w:pPr><w:keepNext/><w:spacing w:before="160" w:after="40"/><w:outlineLvl w:val="1"/></w:pPr>'
        '<w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/>'
        '<w:pPr><w:keepNext/><w:spacing w:before="120" w:after="40"/><w:outlineLvl w:val="2"/></w:pPr>'
        '<w:rPr><w:b/><w:sz w:val="23"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/>'
        '<w:pPr><w:ind w:left="720"/><w:spacing w:before="60" w:after="60"/></w:pPr>'
        '<w:rPr><w:i/><w:color w:val="555555"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/>'
        '<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:style>'
        '</w:styles>' % W_NS
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="%s">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        '</Types>' % PKG_NS
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="%s">'
        '<Relationship Id="rId1" Type="%s/officeDocument" Target="word/document.xml"/>'
        '<Relationship Id="rId2" Type="%s/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="%s/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>' % (PKG_NS, DOC_NS, PKG_NS, PKG_NS)
    )
    doc_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="%s">'
        '<Relationship Id="rId1" Type="%s/styles" Target="styles.xml"/>'
        '</Relationships>' % (PKG_NS, DOC_NS)
    )
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    core_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:title>\u6cd5\u5f8b\u68c0\u7d22\u62a5\u544a</dc:title>'
        '<dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
        '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified>'
        '</cp:coreProperties>' % (now, now)
    )
    app_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
        '<Application>LegalSearchAgent</Application></Properties>'
    )
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/styles.xml", styles_xml)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
        z.writestr("docProps/core.xml", core_xml)
        z.writestr("docProps/app.xml", app_xml)


def main():
    args = sys.argv[1:]
    make_docx = "--docx" in args
    args = [a for a in args if a != "--docx"]
    if len(args) < 2:
        print("用法: python render_report.py <input.json> <output_dir> [--docx]")
        sys.exit(1)
    inp, outdir = args[0], args[1]
    if not os.path.exists(inp):
        print("输入文件不存在: %s" % inp)
        sys.exit(1)
    os.makedirs(outdir, exist_ok=True)
    with open(inp, encoding="utf-8-sig") as f:
        data = json.load(f)

    md = build_markdown(data)
    base = safe_filename("法律检索_" + (data.get("query", "报告")[:24]))
    md_path = os.path.join(outdir, base + ".md")
    with open(md_path, "w", encoding="utf-8") as w:
        w.write(md)
    out_files = [md_path]
    if make_docx:
        dx = os.path.join(outdir, base + ".docx")
        build_docx(md, dx)
        out_files.append(dx)

    print("已生成检索报告：")
    for p in out_files:
        print("  - " + p)
    print("命中：法条 %d 条 / 类案 %d 篇" %
          (len(data.get("laws", []) or []), len(data.get("cases", []) or [])))


if __name__ == "__main__":
    main()
