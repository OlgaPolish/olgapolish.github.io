#!/usr/bin/env python3
"""Готовит лёгкие версии картинок сайта: AVIF + WebP в нескольких ширинах.

Запуск (из папки MySite):   python _build/optimize_images.py
Нужен Pillow 11.3+ (там AVIF уже встроен):   pip install --upgrade pillow

Файлы создаются рядом с оригиналом:  olha-portrait.jpg → olha-portrait-480.avif, olha-portrait-480.webp, …
Оригиналы (JPG/PNG) не трогаются — они остаются запасным вариантом и для og:image.
Уже готовые файлы пропускаются, если оригинал не менялся.
Новую картинку добавить в IMAGES ниже, потом запустить скрипт и build_*.py.
"""
import os
import sys

from PIL import Image, features

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# путь от корня сайта → ширины, которые нужны
IMAGES = {
    "images/olha-portrait.jpg": (480, 900),
    "images/olha-arbeit.jpg": (550, 1100),
    "images/case-jana-nails.jpg": (600, 1200),
    "images/case-feinschliff.jpg": (600, 1200),
    "images/puzzle-de.jpg": (1024,),
    "images/puzzle-uk.jpg": (1024,),
    "images/puzzle-ru.jpg": (1024,),
    "images/blog/arenda-vs-sobstvennost-de.png": (600, 1200),
    "images/blog/arenda-vs-sobstvennost-uk.png": (600, 1200),
    "images/blog/arenda-vs-sobstvennost-ru.png": (600, 1200),
    "images/blog/put-klientki-de.png": (600, 1200),
    "images/blog/put-klientki-uk.png": (600, 1200),
    "images/blog/put-klientki-ru.png": (600, 1200),
}

# качество: фото чуть сильнее сжимаем, схемы с текстом (PNG) — бережнее
Q = {"photo": {"AVIF": 52, "WEBP": 78}, "chart": {"AVIF": 64, "WEBP": 88}}


def variants(src, widths):
    base, _ = os.path.splitext(src)
    for w in widths:
        for ext in ("avif", "webp"):
            yield w, ext, "%s-%d.%s" % (base, w, ext)


def main():
    if not features.check("avif"):
        sys.exit("В этом Pillow нет AVIF. Обновите:  pip install --upgrade pillow")
    made = skipped = 0
    for rel, widths in IMAGES.items():
        src = os.path.join(ROOT, rel)
        if not os.path.exists(src):
            print("нет файла:", rel)
            continue
        kind = "chart" if rel.endswith(".png") else "photo"
        with Image.open(src) as im:
            im.load()
            im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") and kind == "chart" else "RGB")
            for w, ext, out_rel in variants(rel, widths):
                out = os.path.join(ROOT, out_rel)
                if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
                    skipped += 1
                    continue
                w = min(w, im.width)
                h = round(im.height * w / im.width)
                img = im if w == im.width else im.resize((w, h), Image.LANCZOS)
                fmt = ext.upper()
                opts = {"quality": Q[kind][fmt]}
                if fmt == "WEBP":
                    opts["method"] = 6
                else:
                    opts["speed"] = 6
                img.save(out, fmt, **opts)
                made += 1
                print("%-52s %6.1f KB" % (out_rel, os.path.getsize(out) / 1024))
    print("готово: создано %d, без изменений %d" % (made, skipped))


if __name__ == "__main__":
    main()
