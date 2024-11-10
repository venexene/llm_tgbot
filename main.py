import telebot
import requests
import jsons
from Class_ModelResponse import ModelResponse
from collections import defaultdict

API_TOKEN = 'MY_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

user_contexts = defaultdict(list)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Привет! Я ваш Telegram бот.\n"
        "Доступные команды:\n"
        "/start - вывод всех доступных команд\n"
        "/model - выводит название используемой языковой модели\n"
        "/clear - очистка контекста\n"
        "Отправьте любое сообщение, и я отвечу с помощью LLM модели."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_id = message.from_user.id
    user_contexts[user_id] = []
    bot.reply_to(message, "Контекст очищен")

@bot.message_handler(commands=['model'])
def send_model_name(message):
    response = requests.get('http://localhost:1234/v1/models')

    if response.status_code == 200:
        model_info = response.json()
        model_name = model_info['data'][0]['id']
        bot.reply_to(message, f"Используемая модель: {model_name}")
    else:
        bot.reply_to(message, 'Не удалось получить информацию о модели.')


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_query = message.text

    user_contexts[user_id].append({"role": "user", "content": user_query})

    request = {
        "messages": user_contexts[user_id]
    }

    response = requests.post(
        'http://localhost:1234/v1/chat/completions',
        json=request
    )

    if response.status_code == 200:
        model_response: ModelResponse = jsons.loads(response.text, ModelResponse)
        reply_content = model_response.choices[0].message.content
        user_contexts[user_id].append({"role": "assistant", "content": reply_content})
        bot.reply_to(message, reply_content)
    else:
        bot.reply_to(message, 'Произошла ошибка при обращении к модели.')


if __name__ == '__main__':
    bot.polling(none_stop=True)