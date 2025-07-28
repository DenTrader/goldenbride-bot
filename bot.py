import time
import requests
import os

# === НАСТРОЙКИ ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 60  # интервал проверки в секундах

# Данные для входа
GB_USERNAME = os.getenv("GB_USERNAME")
GB_PASSWORD = os.getenv("GB_PASSWORD")

HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}

session = requests.Session()

def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload)
        if not response.ok:
            print("Telegram error:", response.text)
    except Exception as e:
        print("Error sending Telegram message:", e)

def login():
    try:
        print("🔐 Выполняется вход...")
        login_page = session.get("https://goldenbride.net/lady", headers=HEADERS)
        
        # Получение необходимых параметров можно уточнить при необходимости.
        payload = {
            'email': GB_USERNAME,
            'password': GB_PASSWORD,
            'x': '0',
            'y': '0',
            'remember': 'on'
        }

        response = session.post("https://goldenbride.net/lady/ladysignin", data=payload, headers=HEADERS)
        if "logout" in response.text.lower() or "/lady/logout" in response.text:
            print("✅ Успешный вход")
            return True
        else:
            print("❌ Ошибка входа. Проверь логин/пароль")
            return False
    except Exception as e:
        print("Ошибка авторизации:", e)
        return False

def check_letters():
    try:
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

        response = session.post(
            'https://goldenbride.net/ladymodule/services/rpc',
            data=data,
            headers=headers
        )

        if response.status_code != 200:
            print("HTTP error:", response.status_code)
            return

        response.encoding = 'utf-8'
        text = response.text

        if "+ 1 new" in text or "+ 2 new" in text:
            print("📩 Обнаружено новое письмо")
            send_telegram_message("📬 У вас новое письмо в GoldenBride (раздел Unread).")
        else:
            print("Нет новых писем")

    except Exception as e:
        print("Ошибка при проверке писем:", e)

# === Основной цикл ===
if __name__ == '__main__':
    print("🚀 Запуск бота GoldenBride")

    if login():
        while True:
            check_letters()
            time.sleep(CHECK_INTERVAL)
    else:
        print("⛔️ Бот остановлен из-за ошибки входа")
