import os
from service import Service
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv('.env')
tg_bot = os.getenv('TG_TOKEN')
bot = telebot.TeleBot(tg_bot)

location_messages = {}
svc = Service()

def make_routes_keyboard(routes):
    """Фабрика клавиатуры со списком маршрутов."""
    markup = InlineKeyboardMarkup()
    for rid, full_name in routes.items():
        name = full_name.lstrip('"')
        label = name.split(':', 1)[0]
        btn = InlineKeyboardButton(text=label, callback_data=str(rid))
        markup.add(btn)
    return markup


def build_location_keyboard(route_id: int, idx: int, total: int, detail: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    # 1) Подробнее/Скрыть
    if detail:
        kb.add(InlineKeyboardButton("Скрыть подробности", callback_data=f"loc_{route_id}_{idx}"))
    else:
        kb.add(InlineKeyboardButton("Рассказать поподробнее", callback_data=f"detail_{route_id}_{idx}"))
    # 2) Навигация Prev/Next
    nav_buttons = []
    if idx > 0:
        nav_buttons.append(InlineKeyboardButton("◀ Предыдущая", callback_data=f"loc_{route_id}_{idx-1}"))
    if idx < total - 1:
        nav_buttons.append(InlineKeyboardButton("Следующая ▶", callback_data=f"loc_{route_id}_{idx+1}"))
    if nav_buttons:
        kb.row(*nav_buttons)
    # 3) Меню
    kb.add(InlineKeyboardButton("🏠 В меню", callback_data="back"))
    return kb


@bot.message_handler(commands=['start'])
def start_handler(message):
    """Обработка команды /start: показываем список маршрутов."""
    routes = svc.get_routes_shortly()
    markup = make_routes_keyboard(routes)
    bot.send_message(chat_id=message.chat.id,
                     text="Привет! Выберите маршрут:",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data
    chat_id = call.message.chat.id

    # Возврат в главное меню
    if data == "back":
        if chat_id in location_messages:
            bot.delete_message(chat_id=chat_id, message_id=location_messages[chat_id])
            del location_messages[chat_id]
        routes = svc.get_routes_shortly()
        markup = make_routes_keyboard(routes)
        bot.edit_message_text(chat_id=chat_id,
                              message_id=call.message.message_id,
                              text="Привет! Выберите маршрут:",
                              reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    # Показ подробностей (history) вместо описания
    if data.startswith("detail_"):
        _, r, i = data.split("_", 2)
        route_id, idx = int(r), int(i)
        route = svc.get_route(route_id)
        loc = route.locations[idx]
        text = f"<b>{loc.name}</b>\n\n" + (loc.history or "Подробной информации нет.")
        kb = build_location_keyboard(route_id, idx, len(route.locations), detail=True)
        bot.edit_message_text(chat_id=chat_id,
                              message_id=call.message.message_id,
                              text=text,
                              parse_mode="HTML",
                              reply_markup=kb)
        lat_str, lng_str = map(str.strip, loc.coords.split(",", 1))
        bot.edit_message_live_location(chat_id=chat_id,
                                       message_id=location_messages.get(chat_id),
                                       latitude=float(lat_str),
                                       longitude=float(lng_str))
        bot.answer_callback_query(call.id)
        return

    # Начало маршрута (кратко)
    if data.startswith("start_"):
        route_id = int(data.split("_", 1)[1])
        route = svc.get_route(route_id)
        idx = 0
        loc = route.locations[idx]
        text = f"<b>{loc.name}</b>\n\n{loc.description or 'Описание отсутствует.'}"
        kb = build_location_keyboard(route_id, idx, len(route.locations), detail=False)
        bot.edit_message_text(chat_id=chat_id,
                              message_id=call.message.message_id,
                              text=text,
                              parse_mode="HTML",
                              reply_markup=kb)
        lat_str, lng_str = map(str.strip, loc.coords.split(",", 1))
        loc_msg = bot.send_location(chat_id=chat_id,
                                     latitude=float(lat_str),
                                     longitude=float(lng_str),
                                     live_period=86400)
        location_messages[chat_id] = loc_msg.message_id
        bot.answer_callback_query(call.id)
        return

    # Переход между локациями (кратко)
    if data.startswith("loc_"):
        _, r, i = data.split("_", 2)
        route_id, idx = int(r), int(i)
        route = svc.get_route(route_id)
        loc = route.locations[idx]
        text = f"<b>{loc.name}</b>\n\n{loc.description or 'Описание отсутствует.'}"
        kb = build_location_keyboard(route_id, idx, len(route.locations), detail=False)
        bot.edit_message_text(chat_id=chat_id,
                              message_id=call.message.message_id,
                              text=text,
                              parse_mode="HTML",
                              reply_markup=kb)
        lat_str, lng_str = map(str.strip, loc.coords.split(",", 1))
        bot.edit_message_live_location(chat_id=chat_id,
                                       message_id=location_messages.get(chat_id),
                                       latitude=float(lat_str),
                                       longitude=float(lng_str))
        bot.answer_callback_query(call.id)
        return

    # Выбор маршрута по ID
    try:
        route_id = int(data)
    except ValueError:
        bot.answer_callback_query(call.id, "Неверные данные")
        return

    route = svc.get_route(route_id)
    if not route:
        bot.answer_callback_query(call.id, "Маршрут не найден")
        return

    text = route.description or "Описание недоступно"
    if route.map_link:
        text += f"\n\n🗺 <a href=\"{route.map_link}\">Ссылка на карту</a>"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"),
               InlineKeyboardButton("▶ Начать", callback_data=f"start_{route_id}"))
    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=text,
                          parse_mode="HTML",
                          disable_web_page_preview=False,
                          reply_markup=markup)
    bot.answer_callback_query(call.id)


if __name__ == '__main__':
    print("Bot is starting...")
    bot.infinity_polling()
