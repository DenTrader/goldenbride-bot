import time
import requests
import os

# === НАСТРОЙКИ ===
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CHECK_INTERVAL = 60  # сек

GB_LOGIN = os.getenv('GB_LOGIN')
GB_PASSWORD = os.getenv('GB_PASSWORD')

LOGIN_URL = "https://goldenbride.net/rest/authentication/login"
RPC_URL = "https://goldenbride.net/ladymodule/services/rpc"

session = requests.Session()


def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        r = requests.post(url, json=payload)
        if not r.ok:
            print("Telegram error:", r.text)
    except Exception as e:
        print("Telegram send failed:", e)


def login():
    try:
        print("🔐 Выполняем вход на сайт...")
        resp = session.post(LOGIN_URL, json={
            "email": GB_LOGIN,
            "password": GB_PASSWORD
        })
        if resp.status_code != 200 or "error" in resp.text.lower():
            print("❌ Ошибка входа. Проверь логин/пароль")
            return False
        print("✅ Успешный вход. Получен JSESSIONID:", session.cookies.get("JSESSIONID"))
        return True
    except Exception as e:
        print("Ошибка авторизации:", e)
        return False


def check_letters():
    headers = {
        'Content-Type': 'text/x-gwt-rpc; charset=UTF-8',
        'X-GWT-Permutation': '7',
        'X-GWT-Module-Base': 'https://goldenbride.net/ladymodule/',
        'Origin': 'https://goldenbride.net',
        'Referer': 'https://goldenbride.net/lady',
        'User-Agent': 'Mozilla/5.0'
    }

    data = (
        '7|0|12|https://goldenbride.net/ladymodule/|666169C96E2B407FC0A44C60C63BB0BB|'
        'com.lady.shared.dataaccess.IDataServlet|search|com.lady.shared.search.SearchParams/439098922|I|Z|'
        'com.lady.shared.search.mail.LetterSearchParams/283117212|com.lady.shared.common.LetterDirection/1794437264|'
        'java.lang.Boolean/476441737|java.lang.Integer/3438268394|-sentDate|1|2|3|4|4|5|6|6|7|8|0|0|0|0|9|1|0|0|-1|0|0|10|0|0|1|-3|0|10|1|11|866986|0|0|0|0|0|0|-1|1|0|12|0|0|0|10|1|'
    )

    try:
        r = session.post(RPC_URL, data=data, headers=headers)
        r.encoding = 'utf-8'
        if r.status_code != 200:
            print("HTTP error:", r.status_code)
            return

        text = r.text

        if "+ 1 new" in text or "+ 2 new" in text:
            print("📩 Обнаружено новое письмо")
            send_telegram_message("📬 У вас новое письмо в GoldenBride (раздел Unread).")
        else:
            print("Нет новых писем")
    except Exception as e:
        print("Ошибка при проверке писем:", e)


if __name__ == '__main__':
    print("🚀 Бот GoldenBride запущен")
    if login():
        while True:
            check_letters()
            time.sleep(CHECK_INTERVAL)
