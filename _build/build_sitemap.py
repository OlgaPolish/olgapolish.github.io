# -*- coding: utf-8 -*-
"""sitemap.xml для olhapolishchuk.de с <lastmod>.
Запуск: python _build/build_sitemap.py   (ПОСЛЕ всех build_*.py, перед git add)

Список страниц берётся из сборщиков: главная (build_site), блог (build_blog.POSTS),
лендинги (build_landing.PAGES), чек-лист (build_checklist.SLUG). Новая статья или лендинг
попадают в sitemap сами — вручную sitemap.xml больше не править.

lastmod = дата, когда ГОТОВЫЙ HTML страницы последний раз реально изменился.
Отпечатки (sha256) и даты хранятся в _build/sitemap_dates.json — этот файл коммитить.
Пересборка без изменений дату не трогает. Первый запуск берёт дату последнего git-коммита
файла (если файл с тех пор не менялся), иначе сегодняшнюю.
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_site as B  # noqa: E402
import build_blog  # noqa: E402
import build_landing  # noqa: E402
import build_checklist  # noqa: E402

LANGS = ("de", "uk", "ru")
CACHE = os.path.join(HERE, "sitemap_dates.json")


def groups():
    """Список групп: {lang: относительный путь}. Одна группа = одна страница на разных языках."""
    g = [{l: B.PATHS[l] for l in LANGS}]                                   # главная
    g.append({l: B.PATHS[l] + "blog/" for l in B.BLOG_LANGS})              # список статей
    for p in sorted(build_blog.POSTS, key=lambda x: x["date"]):           # статьи
        g.append({l: B.PATHS[l] + "blog/" + p[l]["slug"] for l in B.BLOG_LANGS if l in p})
    for pg in build_landing.PAGES:                                         # лендинги
        g.append({l: B.PATHS[l] + pg[l]["slug"] for l in LANGS if l in pg})
    g.append({l: B.PATHS[l] + build_checklist.SLUG for l in LANGS})        # чек-лист
    return g


def file_of(root, rel):
    return os.path.join(root, rel + "index.html" if rel == "" or rel.endswith("/") else rel)


def git_date(root, path):
    """Дата последнего коммита файла, если рабочая копия совпадает с HEAD; иначе None."""
    try:
        rel = os.path.relpath(path, root)
        if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=root,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
            return None
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=root,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout.strip()
        return out or None
    except (OSError, ValueError):
        return None


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..")
    today = datetime.date.today().isoformat()
    try:
        with open(CACHE, encoding="utf-8") as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    changed = []
    for grp in groups():
        alts = [(l, B.SITE + rel) for l, rel in grp.items()]
        if "de" in grp:
            alts.append(("x-default", B.SITE + grp["de"]))
        for lang, rel in grp.items():
            path = file_of(root, rel)
            if not os.path.exists(path):
                print("!! нет файла, пропускаю:", rel or "index.html", "— сначала запусти build_*.py")
                continue
            with open(path, "rb") as f:
                h = hashlib.sha256(f.read()).hexdigest()
            old = cache.get(rel)
            if old and old.get("hash") == h:
                date = old["date"]
            else:
                date = (git_date(root, path) if not old else None) or today
                cache[rel] = {"hash": h, "date": date}
                changed.append((rel or "/", date))
            out.append("  <url>")
            out.append("    <loc>%s</loc>" % (B.SITE + rel))
            out.append("    <lastmod>%s</lastmod>" % date)
            for l2, href in alts:
                out.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (l2, href))
            out.append("  </url>")
    out.append("</urlset>")

    with open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    with open(CACHE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("ok sitemap.xml —", sum(1 for l in out if l == "  <url>"), "адресов")
    for rel, date in changed:
        print("   обновлено:", rel, date)


if __name__ == "__main__":
    main()
