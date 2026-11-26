import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

URLS_BTK = ["https://web.archive.org/web/20251006013347/http://jogikerdesek.hu/gyakori-kerdesek/b%C3%BCntet%C5%91jog",
        "https://web.archive.org/web/20251113164931/http://www.jogikerdesek.hu/gyakori-kerdesek/b%C3%BCntet%C5%91jog?start=20",
        "https://web.archive.org/web/20251113164931/http://www.jogikerdesek.hu/gyakori-kerdesek/b%C3%BCntet%C5%91jog?start=40",
        "https://web.archive.org/web/20251113164931/http://www.jogikerdesek.hu/gyakori-kerdesek/b%C3%BCntet%C5%91jog?start=60"]

URLS_SZJA = ["https://web.archive.org/web/20251119044719/http://jogikerdesek.hu/gyakori-kerdesek/ad%C3%B3jogi-tan%C3%A1csad%C3%A1s"]

URLS_PTK = ["https://web.archive.org/web/20260212170234/http://jogikerdesek.hu/gyakori-kerdesek/polg%C3%A1ri-jog"]

URLS_MT = ["https://web.archive.org/web/20260208145515/http://jogikerdesek.hu/gyakori-kerdesek/munkajog",
    "https://web.archive.org/web/20260510045942/http://jogikerdesek.hu/gyakori-kerdesek/munkajog?start=20",
    "https://web.archive.org/web/20260510045942/http://jogikerdesek.hu/gyakori-kerdesek/munkajog?start=40",
    "https://web.archive.org/web/20260510045942/http://jogikerdesek.hu/gyakori-kerdesek/munkajog?start=60",
    "https://web.archive.org/web/20260510045942/http://jogikerdesek.hu/gyakori-kerdesek/munkajog?start=80",
    "https://web.archive.org/web/20260510045942/http://jogikerdesek.hu/gyakori-kerdesek/munkajog?start=100",
    "https://web.archive.org/web/20260510045942/http://jogikerdesek.hu/gyakori-kerdesek/munkajog?start=120",
    "https://web.archive.org/web/20260510045942/http://jogikerdesek.hu/gyakori-kerdesek/munkajog?start=140"
        ]
article_urls = []
questions = [] # kerdes, valasz

for url in URLS_SZJA:
    for s in range(5):
        try:
            response = requests.get(url)
            break
        except:
            if (s != 4):
                print("Szerver hiba, újrapróbálkozás!")
                time.sleep(s * 4)
            else:
                time.sleep(25)
                response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    for div in soup.find_all("div", class_="qa-q-list-item"):
        answer_count = div.find("span", class_="qa-a-count-data")

        if answer_count is None:
            print("Nem található válaszszám!")
            continue

        if answer_count.get_text(strip=True) != "1":
            print(f"Nem érvényes: {div.get('id')}")
            continue

        link = div.select_one(".qa-q-item-title a[href]")

        if link is None:
            print("Nem található kérdéslink!")
            continue

        a_url = urljoin("https://web.archive.org", link["href"])
        article_urls.append(a_url)
time.sleep(30)

print(article_urls)

for i, url in enumerate(article_urls):
    for s in range(5):
        try:
            response = requests.get(url)
            break
        except:
            if (s!=4):
                print("Szerver hiba, újrapróbálkozás!")
                time.sleep(s*4)
            else:
                time.sleep(25)
                response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    divs = soup.find_all("div", class_="qa-q-list-item")
    q_div = soup.find("div", class_="qa-part-q-view")

    if q_div is None:
        print(f"Nem található kérdés: {url}")
        continue

    q_text = q_div.find("div", itemprop="text")

    # A cím megkeresése a heading meglététől függetlenül
    heading = soup.find("div", class_="qa-main-heading")

    if heading is not None:
        title = heading.find("span", itemprop="name")
    else:
        title = soup.find("span", itemprop="name")

    title_text = title.get_text(" ", strip=True) if title else ""
    question_text = q_text.get_text(" ", strip=True) if q_text else ""

    if not title_text and not question_text:
        print(f"Nem található sem cím, sem kérdésszöveg: {url}")
        continue

    kerdes = f"{title_text} {question_text}".strip()
    a_div = soup.find("div", class_="qa-a-list-item")

    if a_div is None:
        print(f"Nem található válasz: {url}")
        continue

    a_text = a_div.find("div", itemprop="text")

    if a_text is None:
        print(f"Nem található válaszszöveg: {url}")
        continue

    # A teljes szöveget kinyerjük, a <br> elemek helyén szóközzel
    valasz = a_text.get_text(" ", strip=True)

    # Üdvözlés eltávolítása
    if "!" in valasz:
        valasz = valasz.split("!", 1)[1].strip()

    # Jogi csapat aláírásának és a disclaimernek az eltávolítása
    disclaimer = "a PROKATOR-NET jogi csapata"

    if disclaimer in valasz:
        valasz = valasz.split(disclaimer, 1)[0].strip()

    if not valasz:
        print(f"Üres válasz: {url}")
        continue
    print(i, url)
    print(kerdes)
    print(valasz)
    print()

    questions.append({"kerdes": kerdes, "valasz": valasz})
    time.sleep(3)
print(questions)
