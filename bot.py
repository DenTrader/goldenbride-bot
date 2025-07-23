import time
import requests

# === НАСТРОЙКИ ===
TELEGRAM_BOT_TOKEN = '8096767666:AAFew8yjw3SfIuCDdJbcX9TXZlfMW2QH-tM'
TELEGRAM_CHAT_ID = '7154393140'
CHECK_INTERVAL = 60  # интервал в секундах

# ⚠️ Cookie вашей авторизованной сессии
COOKIES = {
    'JSESSIONID': '15A5D01CD867B9699BD2411B4A314EBA',
    # добавь другие cookie, если есть
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

def check_letters():
    try:
        response = requests.post(
            'https://goldenbride.net/ladymodule/services/rpc',
            data=DATA_PAYLOAD,
            cookies=COOKIES,
            headers=HEADERS
        )
        if response.status_code != 200:
            print("HTTP error:", response.status_code)
            return

        response.encoding = 'utf-8'  # Явно указываем кодировку
        text = response.text
        
        # Для отладки (можно убрать после уверенности, что работает)
        # print(repr(text))

        if "+ 1 new" in text or "+ 2 new" in text:
            print("📩 Обнаружено новое письмо")
            send_telegram_message("📬 У вас новое письмо в GoldenBride (раздел Unread).")
        else:
            print("Нет новых писем")

    except Exception as e:
        print("Ошибка при проверке писем:", e)

# === Цикл проверки ===
if __name__ == '__main__':
    print("Запущен бот GoldenBride")
    while True:
        check_letters()
        time.sleep(CHECK_INTERVAL)

