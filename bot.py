import time
import requests
import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
JSESSIONID = os.getenv('JSESSIONID')
CHECK_INTERVAL = 60

COOKIES = {
    'JSESSIONID': JSESSIONID
}

HEADERS = {
    'Content-Type': 'text/x-gwt-rpc; charset=UTF-8',
    'X-GWT-Permutation': '7',
    'X-GWT-Module-Base': 'https://goldenbride.net/ladymodule/',
    'Origin': 'https://goldenbride.net',
    'Referer': 'https://goldenbride.net/lady',
    'User-Agent': 'Mozilla/5.0'
}

DATA_PAYLOAD = (
    '7|0|12|https://goldenbride.net/ladymodule/|666169C96E2B407FC0A44C60C63BB0BB|'
    'com.lady.shared.dataaccess.IDataServlet|search|com.lady.shared.search.SearchParams/439098922|I|Z|'
    'com.lady.shared.search.mail.LetterSearchParams/283117212|com.lady.shared.common.LetterDirection/1794437264|'
    'java.lang.Boolean/476441737|java.lang.Integer/3438268394|-sentDate|1|2|3|4|4|5|6|6|7|8|0|0|0|0|9|1|0|0|-1|0|0|10|0|0|1|-3|0|10|1|11|866986|0|0|0|0|0|0|-1|1|0|12|0|0|0|10|1|'
)

def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': text, 'parse_mode': 'HTML'}
    try:
        r = requests.post(url, json=payload)
        if not r.ok:
            print("Ошибка Telegram:", r.text)
    except Exception as e:
        print("Ошибка при отправке:", e)

def check_letters():
    try:
        r = requests.post(
            'https://goldenbride.net/ladymodule/services/rpc',
            data=DATA_PAYLOAD,
            cookies=COOKIES,
            headers=HEADERS
        )
        
        if r.status_code != 200:
            print(f"⚠️ HTTP ошибка: {r.status_code}")
            if r.status_code in [401, 403]:
                send_telegram_message("❗ Cookie устарели. Обновите JSESSIONID в Railway.")
            return

        r.encoding = 'utf-8'
        text = r.text.strip()

        # Если куки устарели — ответ пустой или не содержит ожидаемых данных
        if len(text) < 50 or "login" in text.lower():
            print("⚠️ Похоже, что cookie устарели.")
            send_telegram_message("❗ Cookie устарели. Обновите JSESSIONID в Railway.")
            return

        if "+ 1 new" in text or "+ 2 new" in text:
            print("📩 Новое письмо")
            send_telegram_message("📬 У вас новое письмо в GoldenBride!")
        else:
            print("Нет новых писем")

    except Exception as e:
        print("Ошибка при проверке писем:", e)
        send_telegram_message(f"❗ Ошибка при проверке писем: {e}")

if __name__ == '__main__':
    print("🚀 Бот GoldenBride запущен")
    while True:
        check_letters()
        time.sleep(CHECK_INTERVAL)
