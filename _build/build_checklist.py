#!/usr/bin/env python3
"""Собирает страницу чек-листа «10 проверок профиля в Google Maps» на трёх языках:
/checklist-google-maps.html (DE), /uk/checklist-google-maps.html, /ru/checklist-google-maps.html

Запуск из корня репозитория:  python _build/build_checklist.py
Шрифты и цвета берутся из build_site.py, тексты — в словаре C ниже.
Версия 2 (28.11.2026): галочки со счётчиком (отметки хранятся в браузере),
время и «где нажать» у каждого пункта, примеры правильно/неправильно, оценка результата, FAQ.
"""
import html
import json
import os
import re
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as B  # noqa: E402

SLUG = "checklist-google-maps.html"

# Статьи «7 причин» — на них ссылается вводный блок чек-листа
ARTICLE = {
    "de": "blog/warum-sie-bei-google-maps-nicht-gefunden-werden.html",
    "uk": "uk/blog/chomu-vas-ne-znakhodyat-u-google-maps.html",
    "ru": "ru/blog/pochemu-vas-ne-nakhodyat-v-google-maps.html",
}

# Разметка текста пунктов (body_html):
#   **жирный** · пустая строка = новый абзац · "- " список · "1. " нумерованный
#   "> " блок-шаблон · "+ " пример «правильно» · "x " пример «неправильно»
# Пункт = (заголовок, время, где нажать, текст)

C = {}

C["ru"] = dict(
    title="Чек-лист Google Maps: 10 пунктов с галочками — Olha Polishchuk",
    desc="Отметьте 10 пунктов и узнайте, насколько готов ваш профиль в Google Maps: примеры «правильно/неправильно», где нажать, сколько времени. Бесплатно.",
    h1="Чек-лист профиля Google Maps: 10 пунктов с галочками",
    lead="Около 30 минут. Нужны телефон и Google-аккаунт, через который вы управляете профилем. Отмечайте пункты — счётчик покажет результат.",
    done="Выполнено",
    reset="Сбросить отметки",
    print_btn="Сохранить в PDF / распечатать",
    back="← На главную",
    time_lbl="мин",
    intro="""**Как открыть профиль:** приложение **Google Maps** → фото профиля справа вверху → **«Ваш профиль компании»**. Профиля ещё нет — создайте его на **business.google.com**.""",
    intro_link=("Почему это важно и как Google выбирает, кого показать на карте, — в статье", "«Почему вас не находят в Google Maps: 7 причин»"),
    items=[
        ("1. Название — как на вывеске", 2, "«Изменить профиль» → «Название компании»", """+ Studio Anna
x Studio Anna – Maniküre Gel günstig Düsseldorf

Ключевые слова в названии нарушают правила Google: название могут изменить или заблокировать профиль."""),
        ("2. Основная категория — самая точная", 3, "«Изменить профиль» → «Категория компании»", """+ Nagelstudio (если основной доход — маникюр)
x Schönheitssalon (слишком общая)

Начните вводить слово — Google предложит варианты. Остальные услуги добавьте дополнительными категориями, но не больше 3–4."""),
        ("3. Адрес или зона обслуживания", 3, "«Изменить профиль» → «Местоположение» / «Зона обслуживания»", """+ Клиенты приходят к вам → точный адрес, метка на входе.
+ Вы ездите к клиентам → адрес скрыт, указаны районы или города.
x Адрес знакомых или виртуальный офис."""),
        ("4. Часы работы и праздники", 3, "«Изменить профиль» → «Часы работы» → «Особые часы работы»", """Внесите заранее 24.12, 25.–26.12, 31.12 и 1.1. Закрытая дверь в «открытое» время — частая причина плохих отзывов."""),
        ("5. Телефон и сайт нажимаются", 2, "откройте свой профиль как клиент, в режиме инкогнито", """Нажмите сами «Позвонить» и «Сайт». Сайта нет — поставьте ссылку на WhatsApp или Instagram."""),
        ("6. Описание по шаблону", 10, "«Изменить профиль» → «Описание»", None),
        ("7. Не меньше 10 фото, новые — раз в месяц", 5, "профиль → «Добавить фото»", """Что уже есть: вход снаружи · помещение · ваши работы · вы и команда · логотип.

x Фото из интернета или со стоков — Google и клиенты это замечают."""),
        ("8. Услуги и цены", 10, "«Изменить профиль» → «Услуги» (в некоторых категориях «Товары»)", """+ Maniküre mit Shellac — ab 35 €
x Maniküre — Preis auf Anfrage

Клиентам проще написать, когда они видят порядок цен."""),
        ("9. Отзывы: ссылка и ответы", 5, "«Попросить оставить отзыв» → скопировать ссылку", """Отправьте ссылку 3–5 довольным клиентам. Отвечайте на все отзывы, и на негативные тоже: спокойно, по делу, с решением. Будущие клиенты читают не столько отзыв, сколько ваш ответ."""),
        ("10. Публикация раз в 2 недели", 5, "профиль → «Добавить новость»", """Новая работа, акция, свободные окна на неделе. Поставьте себе повтор в календаре."""),
    ],
    res_title="Ваш результат",
    res=[
        ("9–10 ✓", "Профиль в хорошей форме. Следите за отзывами и публикациями."),
        ("6–8 ✓", "Основа есть, но клиенты пока уходят к конкурентам. Начните с невыполненных пунктов 1–3: они сильнее всего влияют на показы."),
        ("0–5 ✓", "Профиль работает вполсилы. Проще всего начать с бесплатной проверки."),
    ],
    wa_text="Здравствуйте! Прошла чек-лист по Google Maps и хочу бесплатную проверку профиля.",
    cta_title="Проверить профиль за вас?",
    cta_text="Бесплатный Google-Check: посмотрю ваш профиль и пришлю 3–5 конкретных шагов.",
    cta_btn="Написать в WhatsApp",
    faq_title="Частые вопросы",
    faq=[
        ("Сколько ждать результата после изменений?", "Обычно Google обновляет профиль за несколько дней, а изменения в показах видны через 2–4 недели. В профиле есть раздел «Статистика» — сравните цифры до и после."),
        ("Можно ли заплатить Google, чтобы быть выше на карте?", "Обычные места на карте не продаются. Есть рекламные места с пометкой «Реклама», но это отдельная платная услуга."),
        ("Нужен ли сайт, если есть профиль в Google?", "Не обязательно. Но сайт с теми же названием, адресом и телефоном усиливает доверие Google к профилю."),
    ],
)

C["uk"] = dict(
    title="Чек-лист Google Maps: 10 пунктів із галочками — Olha Polishchuk",
    desc="Позначте 10 пунктів і дізнайтеся, наскільки готовий ваш профіль у Google Maps: приклади «правильно/неправильно», де натиснути, скільки часу. Безкоштовно.",
    h1="Чек-лист профілю Google Maps: 10 пунктів із галочками",
    lead="Близько 30 хвилин. Потрібні телефон і Google-акаунт, через який ви керуєте профілем. Позначайте пункти — лічильник покаже результат.",
    done="Виконано",
    reset="Скинути позначки",
    print_btn="Зберегти в PDF / роздрукувати",
    back="← На головну",
    time_lbl="хв",
    intro="""**Як відкрити профіль:** застосунок **Google Maps** → фото профілю праворуч угорі → **«Ваш профіль компанії»**. Профілю ще немає — створіть його на **business.google.com**.""",
    intro_link=("Чому це важливо і як Google обирає, кого показати на карті, — у статті", "«Чому вас не знаходять у Google Maps: 7 причин»"),
    items=[
        ("1. Назва — як на вивісці", 2, "«Редагувати профіль» → «Назва компанії»", """+ Studio Anna
x Studio Anna – Maniküre Gel günstig Düsseldorf

Ключові слова в назві порушують правила Google: назву можуть змінити або заблокувати профіль."""),
        ("2. Основна категорія — найточніша", 3, "«Редагувати профіль» → «Категорія компанії»", """+ Nagelstudio (якщо основний дохід — манікюр)
x Schönheitssalon (надто загальна)

Почніть вводити слово — Google запропонує варіанти. Інші послуги додайте додатковими категоріями, але не більше 3–4."""),
        ("3. Адреса або зона обслуговування", 3, "«Редагувати профіль» → «Місцезнаходження» / «Зона обслуговування»", """+ Клієнти приходять до вас → точна адреса, позначка біля входу.
+ Ви їздите до клієнтів → адресу приховано, вказано райони чи міста.
x Адреса знайомих або віртуальний офіс."""),
        ("4. Години роботи та свята", 3, "«Редагувати профіль» → «Години роботи» → «Особливі години роботи»", """Внесіть заздалегідь 24.12, 25.–26.12, 31.12 і 1.1. Зачинені двері у «відкритий» час — часта причина поганих відгуків."""),
        ("5. Телефон і сайт натискаються", 2, "відкрийте свій профіль як клієнт, у режимі інкогніто", """Натисніть самі «Зателефонувати» і «Сайт». Сайту немає — вкажіть посилання на WhatsApp або Instagram."""),
        ("6. Опис за шаблоном", 10, "«Редагувати профіль» → «Опис»", None),
        ("7. Щонайменше 10 фото, нові — раз на місяць", 5, "профіль → «Додати фото»", """Що вже є: вхід ззовні · приміщення · ваші роботи · ви та команда · логотип.

x Фото з інтернету чи зі стоків — Google і клієнти це помічають."""),
        ("8. Послуги та ціни", 10, "«Редагувати профіль» → «Послуги» (у деяких категоріях «Товари»)", """+ Maniküre mit Shellac — ab 35 €
x Maniküre — Preis auf Anfrage

Клієнтам простіше написати, коли вони бачать рівень цін."""),
        ("9. Відгуки: посилання та відповіді", 5, "«Попросити залишити відгук» → скопіювати посилання", """Надішліть посилання 3–5 задоволеним клієнтам. Відповідайте на всі відгуки, і на негативні теж: спокійно, по суті, з рішенням. Майбутні клієнти читають не так відгук, як вашу відповідь."""),
        ("10. Допис раз на 2 тижні", 5, "профіль → «Додати новину»", """Нова робота, акція, вільні віконця на тижні. Поставте собі повтор у календарі."""),
    ],
    res_title="Ваш результат",
    res=[
        ("9–10 ✓", "Профіль у гарній формі. Стежте за відгуками й дописами."),
        ("6–8 ✓", "Основа є, але клієнти поки йдуть до конкурентів. Почніть із невиконаних пунктів 1–3: вони найбільше впливають на покази."),
        ("0–5 ✓", "Профіль працює вполовину сили. Найпростіше почати з безкоштовної перевірки."),
    ],
    wa_text="Добрий день! Пройшла чек-лист щодо Google Maps і хочу безкоштовну перевірку профілю.",
    cta_title="Перевірити профіль за вас?",
    cta_text="Безкоштовний Google-Check: перегляну ваш профіль і надішлю 3–5 конкретних кроків.",
    cta_btn="Написати у WhatsApp",
    faq_title="Часті запитання",
    faq=[
        ("Скільки чекати результату після змін?", "Зазвичай Google оновлює профіль за кілька днів, а зміни в показах видно через 2–4 тижні. У профілі є розділ «Статистика» — порівняйте цифри до і після."),
        ("Чи можна заплатити Google, щоб бути вище на карті?", "Звичайні місця на карті не продаються. Є рекламні місця з позначкою «Реклама», але це окрема платна послуга."),
        ("Чи потрібен сайт, якщо є профіль у Google?", "Не обов'язково. Але сайт із тими самими назвою, адресою й телефоном посилює довіру Google до профілю."),
    ],
)

C["de"] = dict(
    title="Google-Unternehmensprofil Checkliste: 10 Punkte — Olha Polishchuk",
    desc="Haken Sie 10 Punkte ab und sehen Sie, wie gut Ihr Google-Maps-Profil aufgestellt ist: Richtig-/Falsch-Beispiele, Klickwege, Zeitangaben. Kostenlos.",
    h1="Google-Unternehmensprofil: Checkliste mit 10 Punkten zum Abhaken",
    lead="Dauert etwa 30 Minuten. Sie brauchen Ihr Handy und das Google-Konto, mit dem Sie das Profil verwalten. Haken Sie die Punkte ab – der Zähler zeigt Ihr Ergebnis.",
    done="Erledigt",
    reset="Häkchen zurücksetzen",
    print_btn="Als PDF speichern / drucken",
    back="← Zur Startseite",
    time_lbl="Min.",
    intro="""**So öffnen Sie Ihr Profil:** App **Google Maps** → Profilbild oben rechts → **„Ihr Unternehmensprofil“**. Noch kein Profil? Legen Sie es auf **business.google.com** an.""",
    intro_link=("Warum das wichtig ist und wie Google entscheidet, wen es auf der Karte zeigt, lesen Sie im Artikel", "„Warum Sie bei Google Maps nicht gefunden werden: 7 Gründe“"),
    items=[
        ("1. Name – genau wie auf dem Schild", 2, "„Profil bearbeiten“ → „Name des Unternehmens“", """+ Studio Anna
x Studio Anna – Maniküre Gel günstig Düsseldorf

Suchbegriffe im Namen verstoßen gegen die Google-Richtlinien: Der Name kann geändert oder das Profil gesperrt werden."""),
        ("2. Hauptkategorie – so genau wie möglich", 3, "„Profil bearbeiten“ → „Unternehmenskategorie“", """+ Nagelstudio (wenn Maniküre Ihr Hauptumsatz ist)
x Schönheitssalon (zu allgemein)

Tippen Sie den Anfang ein – Google schlägt passende Kategorien vor. Weitere Leistungen als zusätzliche Kategorien, aber höchstens 3–4."""),
        ("3. Adresse oder Einzugsgebiet", 3, "„Profil bearbeiten“ → „Standort“ / „Einzugsgebiet“", """+ Kundinnen kommen zu Ihnen → genaue Adresse, Markierung am Eingang.
+ Sie fahren zu Ihren Kundinnen → Adresse ausgeblendet, Stadtteile oder Städte angegeben.
x Adresse von Bekannten oder ein virtuelles Büro."""),
        ("4. Öffnungszeiten und Feiertage", 3, "„Profil bearbeiten“ → „Öffnungszeiten“ → „Besondere Öffnungszeiten“", """Tragen Sie 24.12., 25./26.12., 31.12. und 1.1. schon vorab ein. Eine verschlossene Tür zur „geöffneten“ Zeit ist ein häufiger Grund für schlechte Bewertungen."""),
        ("5. Telefon und Website anklickbar", 2, "Profil wie eine Kundin öffnen, im Inkognito-Fenster", """Tippen Sie selbst auf „Anrufen“ und „Website“. Keine Website? Dann verlinken Sie WhatsApp oder Instagram."""),
        ("6. Beschreibung nach Vorlage", 10, "„Profil bearbeiten“ → „Beschreibung“", None),
        ("7. Mindestens 10 Fotos – jeden Monat neue", 5, "Profil → „Fotos hinzufügen“", """Was haben Sie schon? Eingang von außen · Räume · Ihre Arbeiten · Sie und Ihr Team · Logo.

x Fotos aus dem Internet oder von Bildagenturen – Google und Kundinnen merken das."""),
        ("8. Leistungen und Preise", 10, "„Profil bearbeiten“ → „Dienstleistungen“ (je nach Kategorie „Produkte“)", """+ Maniküre mit Shellac – ab 35 €
x Maniküre – Preis auf Anfrage

Kundinnen schreiben eher, wenn sie die Preisspanne kennen."""),
        ("9. Bewertungen: Link teilen und antworten", 5, "„Um Rezensionen bitten“ → Link kopieren", """Schicken Sie den Link an 3–5 zufriedene Kundinnen. Antworten Sie auf jede Bewertung, auch auf negative: ruhig, sachlich, mit einer Lösung. Künftige Kundinnen lesen weniger die Bewertung als Ihre Antwort darauf."""),
        ("10. Alle 2 Wochen ein Beitrag", 5, "Profil → „Neuigkeit hinzufügen“", """Neue Arbeit, Angebot, freie Termine diese Woche. Tragen Sie sich eine Erinnerung in den Kalender ein."""),
    ],
    res_title="Ihr Ergebnis",
    res=[
        ("9–10 ✓", "Ihr Profil ist gut aufgestellt. Bleiben Sie bei Bewertungen und Beiträgen dran."),
        ("6–8 ✓", "Die Basis steht, aber Kundinnen landen noch bei der Konkurrenz. Beginnen Sie mit offenen Punkten aus 1–3: Sie wirken am stärksten auf die Sichtbarkeit."),
        ("0–5 ✓", "Ihr Profil arbeitet mit halber Kraft. Am einfachsten starten Sie mit einem kostenlosen Check."),
    ],
    wa_text="Hallo! Ich habe die Google-Maps-Checkliste durchgearbeitet und möchte einen kostenlosen Profil-Check.",
    cta_title="Soll ich Ihr Profil prüfen?",
    cta_text="Kostenloser Google-Check: Ich schaue mir Ihr Profil an und schicke Ihnen 3–5 konkrete Schritte.",
    cta_btn="Per WhatsApp schreiben",
    faq_title="Häufige Fragen",
    faq=[
        ("Wann sehe ich Ergebnisse?", "Änderungen übernimmt Google meist in wenigen Tagen, Veränderungen bei den Aufrufen sehen Sie nach 2–4 Wochen. Vergleichen Sie im Profil unter „Leistung“ die Zahlen vorher und nachher."),
        ("Kann ich Google bezahlen, um weiter oben zu stehen?", "Die normalen Plätze auf der Karte sind nicht käuflich. Es gibt Anzeigen mit dem Hinweis „Gesponsert“ – das ist ein separates, kostenpflichtiges Angebot."),
        ("Brauche ich eine Website, wenn ich ein Google-Profil habe?", "Nicht zwingend. Eine Website mit demselben Namen, derselben Adresse und Telefonnummer stärkt aber das Vertrauen von Google in Ihr Profil."),
    ],
)

# Шаблон описания для пункта 6 (без изменений с версии 1)
TPL6 = {
    'de': 'Bis zu 750 Zeichen, ohne Links und ohne Großbuchstaben am Stück. Füllen Sie die Vorlage aus:\n\n> **[Name]** — [was Sie tun] in [Stadt / Stadtteil].\n> Wir helfen [wem: Familien, Autofahrern, kleinen Unternehmen …] [bei welchem Anliegen].\n> Unsere Leistungen: [3–5 Hauptleistungen, durch Komma getrennt].\n> Warum Kunden uns wählen: [Jahre Erfahrung / Garantie / schnelle Termine / persönliche Beratung].\n> Wir sprechen [Deutsch, Russisch, Ukrainisch …].\n> Termin per Telefon oder WhatsApp — [Antwort innerhalb einer Stunde / Termine noch heute].\n\n**Beispiel:** „Studio Anna — Kosmetikerin in Düsseldorf-Bilk. Ich helfe Frauen, ihre Haut ohne aggressive Behandlungen zu pflegen. Leistungen: Gesichtsreinigung, Peelings, Gesichtsmassage, Pflege für empfindliche Haut. 8 Jahre Erfahrung, nur zertifizierte Kosmetik. Ich spreche Deutsch, Russisch und Ukrainisch. Termine per Telefon oder WhatsApp — Antwort innerhalb einer Stunde.“',
    'uk': "До 750 знаків, без посилань і великих літер підряд. Заповніть шаблон:\n\n> **[Назва]** — [чим ви займаєтеся] у [місто / район].\n> Ми допомагаємо [кому: сім'ям, власникам авто, малому бізнесу…] [яке завдання вирішуєте].\n> Наші послуги: [3–5 головних послуг через кому].\n> Чому обирають нас: [досвід у роках / гарантія / швидкі терміни / індивідуальний підхід].\n> Говоримо [німецькою, українською, російською…].\n> Записуйтеся телефоном або у WhatsApp — [відповімо за годину / запис на сьогодні].\n\n**Приклад:** «Studio Anna — косметолог у Düsseldorf-Bilk. Допомагаю жінкам доглядати за шкірою без агресивних процедур. Послуги: чистка обличчя, пілінги, масаж обличчя, догляд для чутливої шкіри. 8 років досвіду, працюю лише із сертифікованою косметикою. Говорю німецькою, українською та російською. Запис телефоном або у WhatsApp — відповідаю протягом години.»",
    'ru': 'До 750 знаков, без ссылок и заглавных букв подряд. Заполните шаблон:\n\n> **[Название]** — [чем вы занимаетесь] в [город / район].\n> Мы помогаем [кому: семьям, владельцам авто, малому бизнесу…] [какую задачу решаете].\n> Наши услуги: [3–5 главных услуг через запятую].\n> Почему выбирают нас: [опыт в годах / гарантия / быстрые сроки / индивидуальный подход].\n> Говорим на [немецком, русском, украинском…].\n> Запишитесь по телефону или WhatsApp — [ответим за час / запись на сегодня].\n\n**Пример:** «Studio Anna — косметолог в Düsseldorf-Bilk. Помогаю женщинам ухаживать за кожей без агрессивных процедур. Услуги: чистка лица, пилинги, массаж лица, уход для чувствительной кожи. 8 лет опыта, работаю только с сертифицированной косметикой. Говорю на немецком, русском и украинском. Запись по телефону или в WhatsApp — отвечаю в течение часа.»',
}

CSS = r"""
:root{--ink:#1E2A4A;--ink-soft:#4A5568;--amber:#D48B3A;--amber-light:#E8A84F;--amber-pale:#FDF3E7;--bg:#fff;--bg-soft:#F7F6F4;--line:rgba(30,42,74,0.1)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'DM Sans',sans-serif;color:var(--ink);background:var(--bg-soft);-webkit-font-smoothing:antialiased;line-height:1.7}
a{color:inherit}
.top{background:var(--ink);color:#fff}
.top .in{max-width:820px;margin:0 auto;padding:18px 24px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.top a{text-decoration:none;font-size:14px;color:rgba(255,255,255,.8)}
.top a:hover{color:var(--amber-light)}
.brand{font-family:'DM Serif Display',serif;font-size:18px;color:#fff!important}
.brand span{color:var(--amber-light)}
main{max-width:820px;margin:0 auto;padding:48px 24px 72px}
h1{font-family:'DM Serif Display',serif;font-weight:400;font-size:clamp(1.8rem,4.5vw,2.6rem);line-height:1.15;margin-bottom:14px}
.lead{color:var(--ink-soft);font-size:1.05rem;margin-bottom:22px}
.print{display:inline-block;background:#fff;border:1px solid var(--line);border-radius:8px;padding:10px 16px;font:inherit;font-size:14px;color:var(--ink);cursor:pointer;margin-bottom:36px}
.print:hover{border-color:var(--amber)}
.item{background:#fff;border:1px solid var(--line);border-radius:12px;padding:24px 26px;margin-bottom:16px;break-inside:avoid}
.item.zero{border-left:4px solid var(--amber)}
.item h2{font-family:'DM Sans',sans-serif;font-size:1.12rem;font-weight:600;margin-bottom:10px;display:flex;gap:12px;align-items:flex-start}
.item p{color:var(--ink-soft);margin-bottom:10px}
.item p:last-child{margin-bottom:0}
.item strong{color:var(--ink)}
.item ul,.item ol{color:var(--ink-soft);margin:0 0 10px 22px}
.item li{margin-bottom:6px}
.tpl{background:var(--amber-pale);border-left:3px solid var(--amber);border-radius:6px;padding:14px 18px;margin:0 0 12px;color:var(--ink)}
.tpl div{margin-bottom:4px}
.cta{background:var(--ink);color:#fff;border-radius:14px;padding:30px 28px;margin-top:32px;text-align:center}
.cta h2{font-family:'DM Serif Display',serif;font-weight:400;font-size:1.6rem;margin-bottom:10px}
.cta p{color:rgba(255,255,255,.78);margin-bottom:20px;max-width:52ch;margin-left:auto;margin-right:auto}
.cta a{display:inline-block;background:#25D366;color:#fff;text-decoration:none;font-weight:600;padding:13px 26px;border-radius:8px}
.sig{text-align:center;color:var(--ink-soft);font-size:14px;margin-top:22px}
@media (max-width:600px){main{padding:32px 16px 56px}.item{padding:20px 18px}}
@media print{body{background:#fff}.top,.print,.cta a{display:none}.item{border:1px solid #ccc}.cta{background:#fff;color:var(--ink);border:1px solid #ccc}.cta p{color:var(--ink-soft)}main{padding:0}}

.counter{position:sticky;top:0;z-index:5;background:var(--bg-soft);padding:10px 0 14px;margin-bottom:8px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.counter b{font-size:1.05rem}
.bar{flex:1;min-width:140px;height:8px;background:var(--line);border-radius:6px;overflow:hidden}
.bar i{display:block;height:100%;width:0;background:var(--amber);transition:width .25s}
.tools{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:28px}
.tools .print{margin-bottom:0}
.intro{background:#fff;border:1px solid var(--line);border-left:4px solid var(--amber);border-radius:12px;padding:20px 24px;margin-bottom:16px;color:var(--ink-soft)}
.intro p{margin-bottom:8px}.intro p:last-child{margin-bottom:0}.intro strong{color:var(--ink)}
.item label{cursor:pointer}
.item input[type=checkbox]{flex-shrink:0;width:22px;height:22px;margin-top:3px;accent-color:var(--amber);cursor:pointer}
.item.is-done{border-color:var(--amber);background:var(--amber-pale)}
.meta{font-size:14px;color:var(--ink-soft);margin:-2px 0 12px 34px}
.ex{border-radius:6px;padding:6px 12px;margin:0 0 6px;font-size:15px}
.ex.good{background:#EAF6EE;color:#1E5E34}
.ex.bad{background:#FBECEC;color:#8A2525}
.res{background:#fff;border:1px solid var(--line);border-radius:12px;padding:24px 26px;margin-top:28px}
.res h2,.faq h2{font-family:'DM Serif Display',serif;font-weight:400;font-size:1.5rem;margin-bottom:12px}
.res div{padding:10px 14px;border-radius:8px;margin-bottom:6px;color:var(--ink-soft)}
.res div.on{background:var(--amber-pale);color:var(--ink);font-weight:500}
.res b{display:inline-block;min-width:64px;color:var(--ink)}
.faq{margin-top:32px}
.faq details{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin-bottom:10px}
.faq summary{cursor:pointer;font-weight:600}
.faq details p{color:var(--ink-soft);margin-top:8px}
@media print{.counter,.tools,.reset{display:none}.item.is-done{background:#fff}.faq details{border:0;padding:0}.faq details>*{display:block}}
"""


def inline(s):
    s = html.escape(s, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def body_html(text):
    out = []
    for block in text.strip().split("\n\n"):
        lines = block.split("\n")
        para = []

        def flush():
            if para:
                out.append("<p>%s</p>" % "<br>".join(inline(x) for x in para))
                para.clear()

        i = 0
        while i < len(lines):
            ln = lines[i]
            for pre, tag in (("- ", "ul"), ("1. ", "ol"), ("> ", "tpl"), ("+ ", "good"), ("x ", "bad")):
                if ln.startswith(pre):
                    flush()
                    grp = []
                    while i < len(lines) and lines[i].startswith(pre):
                        grp.append(lines[i][len(pre):])
                        i += 1
                    if tag in ("good", "bad"):
                        mark = "✓ " if tag == "good" else "✗ "
                        out.extend('<p class="ex %s">%s%s</p>' % (tag, mark, inline(g)) for g in grp)
                    elif tag == "tpl":
                        out.append('<div class="tpl">%s</div>' % "".join("<div>%s</div>" % inline(g) for g in grp))
                    else:
                        out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % inline(g) for g in grp), tag))
                    break
            else:
                para.append(ln)
                i += 1
        flush()
    return "\n".join(out)


JS = r"""
(function(){
  var KEY='olha-checklist-v2', boxes=[].slice.call(document.querySelectorAll('.item input[type=checkbox]'));
  var n=document.getElementById('cnt'), bar=document.getElementById('bar'), rows=document.querySelectorAll('.res div[data-min]');
  var st={}; try{st=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
  function upd(){
    var k=0; boxes.forEach(function(b){ if(b.checked)k++; b.closest('.item').classList.toggle('is-done',b.checked); st[b.id]=b.checked; });
    n.textContent=k; bar.style.width=(k*10)+'%';
    [].forEach.call(rows,function(r){ r.classList.toggle('on', k>=+r.dataset.min && k<=+r.dataset.max); });
    try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}
  }
  boxes.forEach(function(b){ if(st[b.id])b.checked=true; b.addEventListener('change',function(){ upd(); if(b.checked && window.umami){try{umami.track('checklist-punkt',{n:b.id})}catch(e){}} }); });
  var r=document.getElementById('reset'); if(r)r.addEventListener('click',function(){ boxes.forEach(function(b){b.checked=false}); upd(); });
  upd();
})();
"""

RES_RANGES = [(9, 10), (6, 8), (0, 5)]


def render(lang):
    c = C[lang]
    url = B.SITE + B.PATHS[lang] + SLUG
    wa = "https://wa.me/%s?text=%s" % (B.WA_NUM, quote(c["wa_text"]))
    e = html.escape
    w = []
    w.append('<!DOCTYPE html>\n<html lang="%s">\n<head>\n<meta charset="UTF-8">\n<link rel="icon" href="/favicon.ico" sizes="48x48">\n<link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n<link rel="manifest" href="/site.webmanifest">\n' % lang)
    w.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
    w.append('<title>%s</title>\n<meta name="description" content="%s">\n' % (e(c["title"]), e(c["desc"])))
    w.append('<link rel="canonical" href="%s">\n' % url)
    w.append('<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (e(c["title"]), e(c["desc"])))
    w.append('<meta property="og:url" content="%s">\n<meta property="og:image" content="%simages/olha-portrait.jpg">\n<meta property="og:type" content="article">\n' % (url, B.SITE))
    for l2 in ("de", "uk", "ru"):
        w.append('<link rel="alternate" hreflang="%s" href="%s%s%s">\n' % (l2, B.SITE, B.PATHS[l2], SLUG))
    w.append('<link rel="alternate" hreflang="x-default" href="%s%s">\n' % (B.SITE, SLUG))
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": lang, "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c["faq"]]}
    w.append('<script type="application/ld+json">%s</script>\n' % json.dumps(faq_ld, ensure_ascii=False))
    w.append('<style>\n' + B.FONTS + CSS + '</style>\n' + B.analytics_html() + '</head>\n<body>\n')
    w.append('<div class="top"><div class="in"><a class="brand" href="/%s">Olha <span>Polishchuk</span></a><a href="/%s">%s</a></div></div>\n' % (B.PATHS[lang], B.PATHS[lang], e(c["back"])))
    w.append('<main>\n<h1>%s</h1>\n<p class="lead">%s</p>\n' % (e(c["h1"]), e(c["lead"])))
    total = len(c["items"])
    w.append('<div class="counter" aria-live="polite"><b>%s: <span id="cnt">0</span> / %d</b><span class="bar"><i id="bar"></i></span></div>\n' % (e(c["done"]), total))
    w.append('<div class="tools"><button class="print" type="button" onclick="window.print()">%s</button><button class="print reset" id="reset" type="button">%s</button></div>\n' % (e(c["print_btn"]), e(c["reset"])))
    pre, link_txt = c["intro_link"]
    w.append('<div class="intro">%s\n<p><em>%s <a href="/%s">%s</a>.</em></p></div>\n' % (body_html(c["intro"]), e(pre), ARTICLE[lang], e(link_txt)))
    for n, (h, mins, where, txt) in enumerate(c["items"], 1):
        if txt is None:
            txt = TPL6[lang]
        w.append('<section class="item"><h2><input type="checkbox" id="p%d"><label for="p%d">%s</label></h2>\n<p class="meta">⏱ %d %s · 📍 %s</p>\n%s\n</section>\n' % (
            n, n, e(h), mins, e(c["time_lbl"]), e(where), body_html(txt)))
    w.append('<div class="res"><h2>%s</h2>\n' % e(c["res_title"]))
    for (lo, hi), (lbl, txt) in zip(RES_RANGES, c["res"]):
        w.append('<div data-min="%d" data-max="%d"><b>%s</b> %s</div>\n' % (lo, hi, e(lbl), e(txt)))
    w.append('</div>\n')
    w.append('<div class="cta"><h2>%s</h2><p>%s</p><a href="%s" target="_blank" rel="noopener">%s</a></div>\n' % (
        e(c["cta_title"]), e(c["cta_text"]), e(wa), e(c["cta_btn"])))
    w.append('<div class="faq"><h2>%s</h2>\n' % e(c["faq_title"]))
    for q, a in c["faq"]:
        w.append('<details><summary>%s</summary><p>%s</p></details>\n' % (e(q), e(a)))
    w.append('</div>\n')
    w.append('<p class="sig">Olha Polishchuk · <a href="/%s">olhapolishchuk.de</a></p>\n</main>\n<script>%s</script>\n</body>\n</html>\n' % (B.PATHS[lang], JS))
    return "".join(w).replace(" €", " €")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    for lang in ("de", "uk", "ru"):
        d = os.path.join(root, B.PATHS[lang])
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, SLUG)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(render(lang))
        print("ok", lang, p)


if __name__ == "__main__":
    main()
