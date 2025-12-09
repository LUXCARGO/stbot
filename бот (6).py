import requests
import re
import time

TOKEN = "8531099499:AAFpaRieIzA-w9FtBrMQ3s6oYRdMNlgWPsw"
API_URL = f"https://api.telegram.org/bot{TOKEN}/"
ADMIN_ID = 7849292154  # Ваш Telegram ID
CHANNEL_ID = "@wzzocc"  # username канала или ID

# --- Хранилище блоков ---
data_blocks = []

# --- Функции ---
def send_message(chat_id, text):
    requests.get(API_URL + "sendMessage", params={"chat_id": chat_id, "text": text})

def normalize_text(text):
    return re.sub(r'\W', '', text).lower()

def wait_for_admin_input(offset):
    """Ждём ответа от админа."""
    while True:
        params = {"timeout": 100, "offset": offset}
        updates = requests.get(API_URL + "getUpdates", params=params).json()
        for update in updates.get("result", []):
            offset = update["update_id"] + 1
            if "message" not in update:
                continue
            message = update["message"]
            user_id = message["from"]["id"]
            if user_id != ADMIN_ID:
                continue
            return message.get("text", ""), offset

def add_block(offset):
    """Добавляем новый блок."""
    send_message(ADMIN_ID, "Введите вопрос:")
    question, offset = wait_for_admin_input(offset)

    send_message(ADMIN_ID, "Введите ответ:")
    answer, offset = wait_for_admin_input(offset)

    block = {"question": question, "answer": answer}
    data_blocks.append(block)

    # Отправка в канал
    send_message(CHANNEL_ID, f"Вопрос:   {question}\n\nОтвет:   {answer}")

    send_message(ADMIN_ID, "Блок добавлен и отправлен в канал!")
    return offset

# --- Основной цикл ---
def main():
    offset = None

    while True:
        params = {"timeout": 100, "offset": offset}
        response = requests.get(API_URL + "getUpdates", params=params).json()

        for update in response.get("result", []):
            offset = update["update_id"] + 1

            if "message" not in update:
                continue

            message = update["message"]
            chat_id = message["chat"]["id"]
            user_id = message["from"]["id"]
            text = message.get("text", "")

            # --- Команда добавления блока (только для админа) ---
            if text == "/addblock" and user_id == ADMIN_ID:
                offset = add_block(offset)
                continue

            # --- Поиск для всех пользователей ---
            query_norm = normalize_text(text)
            results = []

            for block in data_blocks:
                q_norm = normalize_text(block["question"])
                a_norm = normalize_text(block["answer"])
                key = "".join([w[0] for w in block["question"].split()])
                key_norm = normalize_text(key)

                if (query_norm in q_norm or
                    query_norm in a_norm or
                    query_norm == key_norm):
                    results.append(f"Вопрос:   {block['question']}\n\nОтвет:   {block['answer']}")

            if results:
                send_message(chat_id, "\n\n".join(results))
            else:
                send_message(chat_id, "Ничего не найдено.")

# --- Запуск ---
if __name__ == "__main__":
    main()
