import os
from service import Service
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv('.env')
tg_bot = os.getenv('TG_TOKEN')
bot = telebot.TeleBot(tg_bot)

# Создаём сервис один раз
svc = Service()
print(svc.get_route(1).description)

def make_routes_keyboard(routes):
    """Фабрика клавиатуры со списком маршрутов."""
    markup = InlineKeyboardMarkup()
    for rid, full_name in routes.items():
        # 1) Убираем начальную кавычку, если она есть
        if full_name.startswith('"'):
            name = full_name[1:]
        else:
            name = full_name

        # 2) Берём часть до двоеточия (split ':' вернёт список из двух частей, нам нужен [0])
        label = name.split(':', 1)[0]

        btn = telebot.types.InlineKeyboardButton(text=label, callback_data=str(rid))
        markup.add(btn)
    return markup

def make_location_keyboard(route_id: int, idx: int, total: int) -> InlineKeyboardMarkup:
    """
    Собираем клавиатуру для локации:
    – «◀ Предыдущая» (если не первая),
    – «Следующая ▶» (если не последняя),
    – «🏠 В меню» (возврат к списку маршрутов).
    """
    kb = InlineKeyboardMarkup()
    buttons = []

    if idx > 0:
        buttons.append(InlineKeyboardButton("◀ Предыдущая", callback_data=f"loc_{route_id}_{idx-1}"))
    if idx < total - 1:
        buttons.append(InlineKeyboardButton("Следующая ▶", callback_data=f"loc_{route_id}_{idx+1}"))

    # Отдельная строка для возврата в список маршрутов
    kb.row(*buttons)
    kb.add(InlineKeyboardButton("🏠 В меню", callback_data="back"))
    return kb

@bot.message_handler(commands=['start'])
def start_handler(message):
    routes = svc.get_routes_shortly()
    markup = make_routes_keyboard(routes)
    bot.send_message(
        chat_id=message.chat.id,
        text="Привет! Выберите маршрут:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data

    # Если нажали "Назад" — пересоздаём список маршрутов
    if data == "back":
        routes = svc.get_routes_shortly()
        markup = make_routes_keyboard(routes)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Привет! Выберите маршрут:",
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
        return

    # 2) Начать маршрут — сразу локация 0
    if data.startswith("start_"):
        route_id = int(data.split("_", 1)[1])
        route = svc.get_route(route_id)
        # сразу показываем первую локацию
        idx = 0
        loc = route.locations[idx]
        text = f"<b>{loc.name}</b>\n\n{loc.description or 'Описание отсутствует.'}"
        if loc.history:
            text += f"\n\n🕰 {loc.history}"
        kb = make_location_keyboard(route_id, idx, len(route.locations))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="HTML",
            reply_markup=kb
        )
        return bot.answer_callback_query(call.id)

    # 3) Навигация по локациям
    if data.startswith("loc_"):
        _, r, i = data.split("_", 2)
        route_id = int(r)
        idx = int(i)
        route = svc.get_route(route_id)
        loc = route.locations[idx]
        # Формируем текст локации
        text = f"<b>{loc.name}</b>\n\n"
        text += loc.description or "Описание отсутствует."
        if loc.history:
            text += f"\n\n🕰 {loc.history}"
        # Кнопки
        kb = make_location_keyboard(route_id, idx, len(route.locations))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="HTML",
            reply_markup=kb
        )
        return bot.answer_callback_query(call.id)

    # Иначе — это id маршрута
    try:
        route_id = int(data)
    except ValueError:
        bot.answer_callback_query(call.id, "Неверные данные")
        return

    route = svc.get_route(route_id)
    if not route:
        bot.answer_callback_query(call.id, "Маршрут не найден")
        return

    # Формируем текст описания + ссылка на карту
    text = route.description or "Описание недоступно"
    if route.map_link:
        text += f"\n\n🗺 <a href=\"{route.map_link}\">Ссылка на карту</a>"

    # Добавляем кнопку «Назад»
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("⬅ Назад", callback_data="back"),
        InlineKeyboardButton("▶ Начать", callback_data=f"start_{route_id}")
    )

    # Редактируем сообщение
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=False,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

if __name__ == '__main__':
    bot.infinity_polling()

