#!/usr/bin/env python3
"""Сообщает Bing (и Yandex, Seznam, Naver) об обновлённых страницах через IndexNow.

Запуск из корня репозитория ПОСЛЕ git push (подождать 1-2 минуты, пока GitHub Pages обновится):
    python _build/indexnow.py            -> отправить все страницы из sitemap.xml
    python _build/indexnow.py /ru/ /uk/  -> отправить только указанные страницы
Ключ лежит в корне сайта: f006a82a0d944938bf1d5e2883cbdb2b.txt (не удалять).
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

HOST = "olhapolishchuk.de"
SITE = "https://olhapolishchuk.de"
KEY = "f006a82a0d944938bf1d5e2883cbdb2b"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def urls_from_sitemap():
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", f.read())


def main():
    if len(sys.argv) > 1:
        urls = [SITE + (a if a.startswith("/") else "/" + a) for a in sys.argv[1:]]
    else:
        urls = urls_from_sitemap()
    body = json.dumps({"host": HOST, "key": KEY,
                       "keyLocation": "%s/%s.txt" % (SITE, KEY),
                       "urlList": urls}).encode("utf-8")
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    print("Отправляю %d адресов:" % len(urls))
    for u in urls:
        print("  " + u)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("Готово, ответ %s (200 или 202 = принято)" % r.status)
    except urllib.error.HTTPError as e:
        hint = {400: "неверный запрос", 403: "ключ не найден на сайте - сделан ли git push?",
                422: "адреса не с этого сайта", 429: "слишком часто, попробуйте позже"}.get(e.code, "")
        print("Ошибка %s %s" % (e.code, hint))
        sys.exit(1)


if __name__ == "__main__":
    main()
