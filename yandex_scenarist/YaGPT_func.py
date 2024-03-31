import requests
from config import *
from telebot import types


def create_prompt(user_data):
    # Начальный текст для нашей истории - это типа вводная часть
    prompt = SYSTEM_PROMPT

    # Добавляем в начало истории инфу о жанре и главном герое, которых выбрал пользователь
    prompt += (f"\nНапиши начало истории в стиле {user_data[0][5]} "
              f"с главным героем {user_data[0][3]}. "
              f"Вот начальный сеттинг: \n{user_data[0][4]}. \n"
              "Начало должно быть коротким, 1-3 предложения.\n")

    # Если пользователь указал что-то еще в "дополнительной информации", добавляем это тоже
    if user_data[0][6]:
        prompt += (f"Также пользователь попросил учесть "
                   f"следующую дополнительную информацию: {user_data[0][6]} ")

    # Добавляем к prompt напоминание не давать пользователю лишних подсказок
    prompt += 'Не пиши никакие подсказки пользователю, что делать дальше. Он сам знает'

    # Возвращаем сформированный текст истории
    return prompt

# Функция для запроса к YandexGPT
def ask_gpt(collection, mode='continue'):

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
        "completionOptions": {"stream": False, "temperature": MODEL_TEMPERATURE, "maxTokens": MAX_MODEL_TOKENS},
        "messages": []
    }

    for row in collection:
        content = row['content']
        if mode == 'continue' and row['role'] == 'user':
            content += '\n' + CONTINUE_STORY
        elif mode == 'end' and row['role'] == 'user':
            content += '\n' + END_STORY
        data["messages"].append({"role": row["role"], "text": content})

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            return f"Status code {response.status_code}."
        return response.json()['result']['alternatives'][0]['message']['text']
    except Exception as e:
        return "Произошла непредвиденная ошибка."
def set(n):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in n:
        btn = types.KeyboardButton(i)
        markup.add(btn)
    return markup
def count_tokens(text: str) -> int:
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
            json={"modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest", "text": text},
            headers=headers
        ).json()['tokens']
    )
