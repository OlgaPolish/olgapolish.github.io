#!/usr/bin/env python3
"""Собирает страницу чек-листа «10 проверок профиля в Google Maps» на трёх языках:
/checklist-google-maps.html (DE), /uk/checklist-google-maps.html, /ru/checklist-google-maps.html

Запуск из корня репозитория:  python _build/build_checklist.py
Шрифты и цвета берутся из build_site.py, тексты — в словаре C ниже.
Разметка текста: **жирный**, пустая строка = новый абзац, строки с "- " = список,
строки с "1. " = нумерованный список, строки с "> " = блок-шаблон.
"""
import html
import os
import re
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as B  # noqa: E402

SLUG = "checklist-google-maps.html"

C = {}

C["ru"] = dict(
    title="Чек-лист: 10 проверок профиля в Google Maps — Olha Polishchuk",
    desc="Бесплатный чек-лист для малого бизнеса: как за 20 минут проверить и улучшить свой профиль компании в Google Maps.",
    h1="Чек-лист: 10 проверок вашего профиля в Google Maps",
    lead="Займёт 20 минут. Вам понадобится телефон и Google-аккаунт, на который зарегистрирован профиль.",
    print_btn="Сохранить в PDF / распечатать",
    back="← На главную",
    wa_text="Здравствуйте! Прочитал(а) чек-лист по Google Maps и хочу бесплатную проверку профиля.",
    cta_title="Хотите, чтобы я проверила ваш профиль?",
    cta_text="Напишите мне в WhatsApp. Первая проверка бесплатная — в ответ пришлю короткий список того, что исправить.",
    cta_btn="Написать в WhatsApp",
    items=[
        ("Шаг 0. Почему это важно и как открыть профиль", """Когда человек ищет «парикмахер рядом», «Steuerberater Düsseldorf» или «ремонт телефонов», Google первым делом показывает карту с тремя компаниями — и только под ней сайты. Попасть в эту тройку можно бесплатно: через профиль компании в Google (Google Unternehmensprofil). Если профиля нет или он заполнен наполовину, клиенты уходят к соседу.

**Как открыть свой профиль:**
1. Войдите в Google-аккаунт, на который зарегистрирован бизнес.
1. Откройте приложение **Google Maps**, нажмите на свою аватарку справа вверху и выберите **«Ваш профиль компании»**. Или наберите в поиске Google название своей компании — если вы владелец, над результатом появится панель управления профилем.
1. Если профиля нет — создайте его на **business.google.com**. Google подтвердит, что компания ваша: по телефону, видео или письмом."""),
        ("1. Название — ровно как на вывеске", "Без добавок вроде «лучший» или «дёшево Düsseldorf». За это Google может заблокировать профиль."),
        ("2. Основная категория — самая точная", "Выберите ту, что точнее всего описывает ваше главное занятие: не «Магазин», а «Магазин детской одежды»; не «Услуги», а «Бухгалтер». Именно основная категория сильнее всего влияет на то, по каким запросам вас показывают. Остальные направления добавьте как дополнительные категории."),
        ("3. Адрес и зона обслуживания", "Если клиенты приходят к вам — точный адрес и метка на правильном месте. Если вы выезжаете к клиентам — адрес можно скрыть и указать районы или города."),
        ("4. Часы работы актуальны, включая праздники", "Закрытая дверь в «открытое» время — частая причина плохих отзывов. Особые часы на праздники выставляйте заранее."),
        ("5. Телефон и сайт кликабельны", "Проверьте сами: нажмите «Позвонить» и «Сайт». Если сайта нет — укажите ссылку на WhatsApp или Instagram."),
        ("6. Описание по шаблону", """До 750 знаков, без ссылок и заглавных букв подряд. Заполните шаблон:

> **[Название]** — [чем вы занимаетесь] в [город / район].
> Мы помогаем [кому: семьям, владельцам авто, малому бизнесу…] [какую задачу решаете].
> Наши услуги: [3–5 главных услуг через запятую].
> Почему выбирают нас: [опыт в годах / гарантия / быстрые сроки / индивидуальный подход].
> Говорим на [немецком, русском, украинском…].
> Запишитесь по телефону или WhatsApp — [ответим за час / запись на сегодня].

**Пример:** «Studio Anna — косметолог в Düsseldorf-Bilk. Помогаю женщинам ухаживать за кожей без агрессивных процедур. Услуги: чистка лица, пилинги, массаж лица, уход для чувствительной кожи. 8 лет опыта, работаю только с сертифицированной косметикой. Говорю на немецком, русском и украинском. Запись по телефону или в WhatsApp — отвечаю в течение часа.»"""),
        ("7. Не меньше 10 свежих фото", "Вход снаружи (чтобы вас легко было найти), помещение, ваши работы или товары, вы и команда. Профили с фото получают заметно больше переходов. Добавляйте новые хотя бы раз в месяц."),
        ("8. Услуги и цены заполнены", """**Как открыть:** в профиле нажмите **«Изменить профиль» → «Услуги»** (в некоторых категориях раздел называется **«Товары»** или **«Меню»**). Нажмите **«Добавить услугу»**, укажите название, цену (можно «от …») и короткое описание.

Клиенту проще написать, когда он понимает порядок цен."""),
        ("9. Отзывы: негативные тоже работают на вас", """Попросите 3–5 довольных клиентов оставить отзыв и дайте им прямую ссылку — её можно взять в профиле: кнопка **«Попросить оставить отзыв»**.

**Не бойтесь негативных отзывов.** Профиль только с пятёрками выглядит подозрительно — люди этому не верят. Будущий клиент читает не столько сам отзыв, сколько ваш ответ на него.
- Отвечайте спокойно, вежливо и по делу: поблагодарите, объясните ситуацию, предложите решение.
- Не спорьте и не оправдывайтесь эмоционально.
- Компетентный ответ на критику убеждает лучше десятка пятёрок: клиент видит, что если что-то пойдёт не так, вы решите вопрос.

Отвечайте и на хорошие отзывы — короткое «Спасибо, рады были помочь!» показывает, что за профилем стоит живой человек."""),
        ("10. Публикации раз в 2 недели", "Новость, акция, фото новой работы. Профиль выглядит «живым», и у клиента появляется повод выбрать вас."),
    ],
)

C["uk"] = dict(
    title="Чек-лист: 10 перевірок профілю в Google Maps — Olha Polishchuk",
    desc="Безкоштовний чек-лист для малого бізнесу: як за 20 хвилин перевірити й покращити профіль компанії в Google Maps.",
    h1="Чек-лист: 10 перевірок вашого профілю в Google Maps",
    lead="Займе 20 хвилин. Знадобиться телефон і Google-акаунт, на який зареєстровано профіль.",
    print_btn="Зберегти в PDF / роздрукувати",
    back="← На головну",
    wa_text="Добрий день! Прочитав(ла) чек-лист щодо Google Maps і хочу безкоштовну перевірку профілю.",
    cta_title="Хочете, щоб я перевірила ваш профіль?",
    cta_text="Напишіть мені у WhatsApp. Перша перевірка безкоштовна — у відповідь надішлю короткий список того, що виправити.",
    cta_btn="Написати у WhatsApp",
    items=[
        ("Крок 0. Чому це важливо і як відкрити профіль", """Коли людина шукає «перукар поруч», «Steuerberater Düsseldorf» чи «ремонт телефонів», Google насамперед показує карту з трьома компаніями — і лише під нею сайти. Потрапити в цю трійку можна безкоштовно: через профіль компанії в Google (Google Unternehmensprofil). Якщо профілю немає або він заповнений наполовину, клієнти йдуть до сусіда.

**Як відкрити свій профіль:**
1. Увійдіть у Google-акаунт, на який зареєстровано бізнес.
1. Відкрийте застосунок **Google Maps**, натисніть на свою аватарку праворуч угорі й оберіть **«Ваш профіль компанії»**. Або введіть у пошуку Google назву своєї компанії — якщо ви власник, над результатом з'явиться панель керування профілем.
1. Якщо профілю немає — створіть його на **business.google.com**. Google підтвердить, що компанія ваша: телефоном, відео або листом."""),
        ("1. Назва — точно як на вивісці", "Без додатків на кшталт «найкращий» чи «дешево Düsseldorf». За це Google може заблокувати профіль."),
        ("2. Основна категорія — найточніша", "Оберіть ту, що найточніше описує ваше головне заняття: не «Магазин», а «Магазин дитячого одягу»; не «Послуги», а «Бухгалтер». Саме основна категорія найбільше впливає на те, за якими запитами вас показують. Інші напрями додайте як додаткові категорії."),
        ("3. Адреса та зона обслуговування", "Якщо клієнти приходять до вас — точна адреса й позначка в правильному місці. Якщо ви виїжджаєте до клієнтів — адресу можна приховати й указати райони чи міста."),
        ("4. Години роботи актуальні, включно зі святами", "Зачинені двері у «відкритий» час — часта причина поганих відгуків. Особливі години на свята виставляйте заздалегідь."),
        ("5. Телефон і сайт клікабельні", "Перевірте самі: натисніть «Зателефонувати» і «Сайт». Якщо сайту немає — вкажіть посилання на WhatsApp або Instagram."),
        ("6. Опис за шаблоном", """До 750 знаків, без посилань і великих літер підряд. Заповніть шаблон:

> **[Назва]** — [чим ви займаєтеся] у [місто / район].
> Ми допомагаємо [кому: сім'ям, власникам авто, малому бізнесу…] [яке завдання вирішуєте].
> Наші послуги: [3–5 головних послуг через кому].
> Чому обирають нас: [досвід у роках / гарантія / швидкі терміни / індивідуальний підхід].
> Говоримо [німецькою, українською, російською…].
> Записуйтеся телефоном або у WhatsApp — [відповімо за годину / запис на сьогодні].

**Приклад:** «Studio Anna — косметолог у Düsseldorf-Bilk. Допомагаю жінкам доглядати за шкірою без агресивних процедур. Послуги: чистка обличчя, пілінги, масаж обличчя, догляд для чутливої шкіри. 8 років досвіду, працюю лише із сертифікованою косметикою. Говорю німецькою, українською та російською. Запис телефоном або у WhatsApp — відповідаю протягом години.»"""),
        ("7. Щонайменше 10 свіжих фото", "Вхід ззовні (щоб вас легко було знайти), приміщення, ваші роботи чи товари, ви та команда. Профілі з фото отримують помітно більше переходів. Додавайте нові хоча б раз на місяць."),
        ("8. Послуги й ціни заповнені", """**Як відкрити:** у профілі натисніть **«Редагувати профіль» → «Послуги»** (у деяких категоріях розділ називається **«Товари»** або **«Меню»**). Натисніть **«Додати послугу»**, вкажіть назву, ціну (можна «від …») і короткий опис.

Клієнтові простіше написати, коли він розуміє рівень цін."""),
        ("9. Відгуки: негативні теж працюють на вас", """Попросіть 3–5 задоволених клієнтів залишити відгук і дайте їм пряме посилання — його можна взяти в профілі: кнопка **«Попросити залишити відгук»**.

**Не бійтеся негативних відгуків.** Профіль лише з п'ятірками виглядає підозріло — люди цьому не вірять. Майбутній клієнт читає не так сам відгук, як вашу відповідь на нього.
- Відповідайте спокійно, ввічливо й по суті: подякуйте, поясніть ситуацію, запропонуйте рішення.
- Не сперечайтеся й не виправдовуйтеся емоційно.
- Компетентна відповідь на критику переконує краще за десяток п'ятірок: клієнт бачить, що коли щось піде не так, ви вирішите питання.

Відповідайте й на хороші відгуки — коротке «Дякуємо, раді були допомогти!» показує, що за профілем стоїть жива людина."""),
        ("10. Дописи раз на 2 тижні", "Новина, акція, фото нової роботи. Профіль виглядає «живим», і в клієнта з'являється привід обрати вас."),
    ],
)

C["de"] = dict(
    title="Checkliste: 10 Punkte für Ihr Google-Maps-Profil — Olha Polishchuk",
    desc="Kostenlose Checkliste für kleine Unternehmen: So prüfen und verbessern Sie Ihr Google-Unternehmensprofil in 20 Minuten.",
    h1="Checkliste: 10 Punkte für Ihr Google-Maps-Profil",
    lead="Dauert etwa 20 Minuten. Sie brauchen Ihr Handy und das Google-Konto, mit dem das Profil verwaltet wird.",
    print_btn="Als PDF speichern / drucken",
    back="← Zur Startseite",
    wa_text="Hallo! Ich habe die Google-Maps-Checkliste gelesen und möchte einen kostenlosen Profil-Check.",
    cta_title="Soll ich Ihr Profil prüfen?",
    cta_text="Schreiben Sie mir per WhatsApp. Der erste Check ist kostenlos — Sie bekommen eine kurze Liste, was Sie verbessern können.",
    cta_btn="Per WhatsApp schreiben",
    items=[
        ("Schritt 0: Warum das wichtig ist und wie Sie Ihr Profil öffnen", """Wer „Friseur in der Nähe“, „Steuerberater Düsseldorf“ oder „Handyreparatur“ sucht, sieht bei Google zuerst eine Karte mit drei Unternehmen — erst darunter kommen Webseiten. In diese Dreiergruppe kommen Sie kostenlos: mit Ihrem Google-Unternehmensprofil. Fehlt das Profil oder ist es nur halb ausgefüllt, gehen die Kunden zur Konkurrenz.

**So öffnen Sie Ihr Profil:**
1. Melden Sie sich mit dem Google-Konto an, auf das Ihr Unternehmen eingetragen ist.
1. Öffnen Sie die App **Google Maps**, tippen Sie oben rechts auf Ihr Profilbild und wählen Sie **„Ihr Unternehmensprofil“**. Oder suchen Sie bei Google nach dem Namen Ihres Unternehmens — als Inhaber sehen Sie über dem Ergebnis ein Feld zur Profilverwaltung.
1. Noch kein Profil? Legen Sie es auf **business.google.com** an. Google bestätigt per Telefon, Video oder Brief, dass das Unternehmen Ihnen gehört."""),
        ("1. Name — genau wie auf dem Schild", "Ohne Zusätze wie „bester“ oder „günstig Düsseldorf“. Dafür kann Google das Profil sperren."),
        ("2. Hauptkategorie — so genau wie möglich", "Wählen Sie die Kategorie, die Ihre Haupttätigkeit am genauesten beschreibt: nicht „Geschäft“, sondern „Kinderbekleidungsgeschäft“; nicht „Dienstleistungen“, sondern „Buchhalter“. Die Hauptkategorie bestimmt am stärksten, bei welchen Suchanfragen Sie erscheinen. Weitere Bereiche fügen Sie als zusätzliche Kategorien hinzu."),
        ("3. Adresse und Einzugsgebiet", "Kommen Kunden zu Ihnen — genaue Adresse und Markierung an der richtigen Stelle. Fahren Sie zu Ihren Kunden — Adresse ausblenden und Stadtteile oder Städte angeben."),
        ("4. Öffnungszeiten aktuell — auch an Feiertagen", "Eine verschlossene Tür zur „geöffneten“ Zeit ist ein häufiger Grund für schlechte Bewertungen. Sonderöffnungszeiten für Feiertage tragen Sie vorab ein."),
        ("5. Telefon und Webseite anklickbar", "Testen Sie selbst: Tippen Sie auf „Anrufen“ und „Website“. Keine Webseite? Dann verlinken Sie WhatsApp oder Instagram."),
        ("6. Beschreibung nach Vorlage", """Bis zu 750 Zeichen, ohne Links und ohne Großbuchstaben am Stück. Füllen Sie die Vorlage aus:

> **[Name]** — [was Sie tun] in [Stadt / Stadtteil].
> Wir helfen [wem: Familien, Autofahrern, kleinen Unternehmen …] [bei welchem Anliegen].
> Unsere Leistungen: [3–5 Hauptleistungen, durch Komma getrennt].
> Warum Kunden uns wählen: [Jahre Erfahrung / Garantie / schnelle Termine / persönliche Beratung].
> Wir sprechen [Deutsch, Russisch, Ukrainisch …].
> Termin per Telefon oder WhatsApp — [Antwort innerhalb einer Stunde / Termine noch heute].

**Beispiel:** „Studio Anna — Kosmetikerin in Düsseldorf-Bilk. Ich helfe Frauen, ihre Haut ohne aggressive Behandlungen zu pflegen. Leistungen: Gesichtsreinigung, Peelings, Gesichtsmassage, Pflege für empfindliche Haut. 8 Jahre Erfahrung, nur zertifizierte Kosmetik. Ich spreche Deutsch, Russisch und Ukrainisch. Termine per Telefon oder WhatsApp — Antwort innerhalb einer Stunde.“"""),
        ("7. Mindestens 10 aktuelle Fotos", "Eingang von außen (damit man Sie leicht findet), Räume, Ihre Arbeiten oder Produkte, Sie und Ihr Team. Profile mit Fotos bekommen deutlich mehr Klicks. Laden Sie mindestens einmal im Monat neue hoch."),
        ("8. Leistungen und Preise ausgefüllt", """**So geht's:** Tippen Sie im Profil auf **„Profil bearbeiten“ → „Dienstleistungen“** (je nach Kategorie heißt der Bereich **„Produkte“** oder **„Speisekarte“**). Dann **„Dienstleistung hinzufügen“** — Name, Preis (auch „ab …“) und eine kurze Beschreibung eintragen.

Kunden schreiben eher, wenn sie die Preisspanne kennen."""),
        ("9. Bewertungen: auch negative arbeiten für Sie", """Bitten Sie 3–5 zufriedene Kunden um eine Bewertung und schicken Sie ihnen den direkten Link — Sie finden ihn im Profil unter **„Um Rezensionen bitten“**.

**Keine Angst vor negativen Bewertungen.** Ein Profil mit nur fünf Sternen wirkt verdächtig — dem glaubt man nicht. Künftige Kunden lesen weniger die Bewertung selbst als Ihre Antwort darauf.
- Antworten Sie ruhig, höflich und sachlich: bedanken, Situation erklären, Lösung anbieten.
- Nicht streiten und nicht emotional rechtfertigen.
- Eine kompetente Antwort auf Kritik überzeugt mehr als zehn Fünf-Sterne-Bewertungen: Der Kunde sieht, dass Sie Probleme lösen, wenn etwas schiefgeht.

Antworten Sie auch auf gute Bewertungen — ein kurzes „Danke, wir haben uns gefreut!“ zeigt, dass hinter dem Profil ein Mensch steht."""),
        ("10. Alle 2 Wochen ein Beitrag", "Neuigkeit, Angebot, Foto einer neuen Arbeit. Das Profil wirkt lebendig — und Kunden haben einen Grund, sich für Sie zu entscheiden."),
    ],
)

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
.box{flex-shrink:0;width:22px;height:22px;border:2px solid var(--amber);border-radius:5px;margin-top:3px}
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
            for pre, tag in (("- ", "ul"), ("1. ", "ol"), ("> ", "tpl")):
                if ln.startswith(pre):
                    flush()
                    grp = []
                    while i < len(lines) and lines[i].startswith(pre):
                        grp.append(lines[i][len(pre):])
                        i += 1
                    if tag == "tpl":
                        out.append('<div class="tpl">%s</div>' % "".join("<div>%s</div>" % inline(g) for g in grp))
                    else:
                        out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % inline(g) for g in grp), tag))
                    break
            else:
                para.append(ln)
                i += 1
        flush()
    return "\n".join(out)


def render(lang):
    c = C[lang]
    url = B.SITE + B.PATHS[lang] + SLUG
    wa = "https://wa.me/%s?text=%s" % (B.WA_NUM, quote(c["wa_text"]))
    w = []
    w.append('<!DOCTYPE html>\n<html lang="%s">\n<head>\n<meta charset="UTF-8">\n' % lang)
    w.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
    w.append('<title>%s</title>\n<meta name="description" content="%s">\n' % (html.escape(c["title"]), html.escape(c["desc"])))
    w.append('<link rel="canonical" href="%s">\n' % url)
    for l2 in ("de", "uk", "ru"):
        w.append('<link rel="alternate" hreflang="%s" href="%s%s%s">\n' % (l2, B.SITE, B.PATHS[l2], SLUG))
    w.append('<link rel="alternate" hreflang="x-default" href="%s%s">\n' % (B.SITE, SLUG))
    w.append('<style>\n' + B.FONTS + CSS + '</style>\n</head>\n<body>\n')
    w.append('<div class="top"><div class="in"><a class="brand" href="/%s">Olha <span>Polishchuk</span></a><a href="/%s">%s</a></div></div>\n' % (B.PATHS[lang], B.PATHS[lang], html.escape(c["back"])))
    w.append('<main>\n<h1>%s</h1>\n<p class="lead">%s</p>\n' % (html.escape(c["h1"]), html.escape(c["lead"])))
    w.append('<button class="print" type="button" onclick="window.print()">%s</button>\n' % html.escape(c["print_btn"]))
    for n, (h, txt) in enumerate(c["items"]):
        cls = "item zero" if n == 0 else "item"
        box = "" if n == 0 else '<span class="box" aria-hidden="true"></span>'
        w.append('<section class="%s"><h2>%s<span>%s</span></h2>\n%s\n</section>\n' % (cls, box, html.escape(h), body_html(txt)))
    w.append('<div class="cta"><h2>%s</h2><p>%s</p><a href="%s" target="_blank" rel="noopener">%s</a></div>\n' % (
        html.escape(c["cta_title"]), html.escape(c["cta_text"]), html.escape(wa), html.escape(c["cta_btn"])))
    w.append('<p class="sig">Olha Polishchuk · <a href="/%s">olhapolishchuk.de</a></p>\n</main>\n</body>\n</html>\n' % B.PATHS[lang])
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
