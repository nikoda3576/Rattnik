import os
import sys
import logging
import subprocess
import time
import socket
import platform
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    filters,
    MessageHandler,
    ConversationHandler
)
import pyautogui
import io
import psutil
import asyncio

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ваши данные
TOKEN = "7778814875:AAHMFjDtwjiac_Kd6UcZ2ftxGqb-b1PKY7U"
AUTHORIZED_USERS = [5556436653]

# Состояния диалога
WAITING_PROCESS_NAME = 1
WAITING_KEY_PRESS = 2
WAITING_KEY_COMBINATION = 3
WAITING_DELETE_CONFIRM = 4

# Клавиатура с командами
COMMAND_KEYBOARD = [
    ["/screenshot", "/deleteprocess"],
    ["/presskey", "/hotkey"],
    ["/systeminfo", "/help"],
    ["/delete"]
]

# Получение информации о системе
def get_system_info():
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = "Недоступен"
        
    return (
        f"🖥️ Система: {platform.system()} {platform.release()}\n"
        f"💻 Имя ПК: {hostname}\n"
        f"📍 IP-адрес: {ip_address}\n"
        f"👤 Пользователь: {os.getlogin()}"
    )

# Отправка уведомления о запуске
async def send_startup_notification():
    try:
        app = Application.builder().token(TOKEN).build()
        await app.initialize()
        for user_id in AUTHORIZED_USERS:
            await app.bot.send_message(
                chat_id=user_id,
                text=f"✅ Система запущена!\n{get_system_info()}",
                reply_markup=ReplyKeyboardMarkup(COMMAND_KEYBOARD, resize_keyboard=True)
            )
        await app.shutdown()
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return
    
    help_text = """
🤖 Бот для удаленного доступа к ПК

Доступные команды:
/screenshot - Скриншот экрана
/deleteprocess - Закрыть процесс
/presskey - Нажать клавишу
/hotkey - Комбинация клавиш
/systeminfo - Информация о системе
/delete - Удалить бота
"""
    await update.message.reply_text(
        help_text,
        reply_markup=ReplyKeyboardMarkup(COMMAND_KEYBOARD, resize_keyboard=True)
    )

async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return
    
    await update.message.reply_text(get_system_info())

async def take_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return
    
    try:
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        await update.message.reply_photo(
            photo=img_byte_arr,
            caption="📸 Скриншот экрана",
            reply_markup=ReplyKeyboardMarkup(COMMAND_KEYBOARD, resize_keyboard=True)
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def delete_process_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "✏️ Введите имя процесса для закрытия (например: notepad.exe):",
        reply_markup=ReplyKeyboardRemove()
    )
    return WAITING_PROCESS_NAME

async def delete_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    process_name = update.message.text.strip().lower()
    killed = []
    
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == process_name:
                proc.kill()
                killed.append(proc.info['name'])
        
        if killed:
            await update.message.reply_text(
                f"✅ Успешно закрыто процессов {len(killed)}: {', '.join(killed)}",
                reply_markup=ReplyKeyboardMarkup(COMMAND_KEYBOARD, resize_keyboard=True)
            )
        else:
            await update.message.reply_text(
                f"⚠️ Процессы с именем '{process_name}' не найдены",
                reply_markup=ReplyKeyboardMarkup(COMMAND_KEYBOARD, resize_keyboard=True)
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при закрытии процесса: {str(e)}")
    
    return ConversationHandler.END

async def press_key_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "⌨️ Введите клавишу для нажатия (например: f, Enter, Escape, Space):",
        reply_markup=ReplyKeyboardRemove()
    )
    return WAITING_KEY_PRESS

async def press_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    key = update.message.text.strip()
    
    try:
        pyautogui.press(key)
        await update.message.reply_text(
            f"✅ Нажата клавиша: {key}",
            reply_markup=ReplyKeyboardMarkup(COMMAND_KEYBOARD, resize_keyboard=True)
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка: {str(e)}\nПопробуйте другое название клавиши.",
            reply_markup=ReplyKeyboardMarkup(COMMAND_KEYBOARD, resize_keyboard=True)
        )
    
    return ConversationHandler.END

async def hotkey_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "⌨️ Введите комбинацию клавиш через '+' (например: ctrl+alt+delete, shift+a):",
        reply_markup=ReplyKeyboardRemove()
    )
    return WAITING_KEY_COMBINATION

async def hotkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    combination = update.message.text.strip()
    
    try:
        keys = combination.split('+')
        pyautogui.hotkey(*keys)
        await update.message.reply_text(
            f"✅ Нажата комбинация: {combination}",
            reply_markup=ReplyKeyboardMarkup(COMMAND_KEYBOARD, resize_keyboard=True)
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка: {str(e)}\nПроверьте правильность формата.",
            reply_markup=ReplyKeyboardMarkup(COMMAND_KEYBOARD, resize_keyboard=True)
        )
    
    return ConversationHandler.END

async def delete_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "⚠️ ВНИМАНИЕ! Это удалит все файлы бота и записи автозагрузки.\n"
        "Отправьте 'ПОДТВЕРЖДАЮ' для удаления:",
        reply_markup=ReplyKeyboardRemove()
    )
    return WAITING_DELETE_CONFIRM

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.strip().upper() != "ПОДТВЕРЖДАЮ":
        await update.message.reply_text(
            "❌ Удаление отменено",
            reply_markup=ReplyKeyboardMarkup(COMMAND_KEYBOARD, resize_keyboard=True)
        )
        return ConversationHandler.END
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        uninstall_script = os.path.join(current_dir, "uninstall.bat")
        
        with open(uninstall_script, "w", encoding="utf-8") as f:
            f.write(f"""
@echo off
echo Удаление бота удаленного доступа...
timeout /t 3 /nobreak >nul

taskkill /f /im pythonw.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1

rd /s /q "{current_dir}" >nul 2>&1
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\RemoteAccessBot.lnk" >nul 2>&1
del "%~f0"
echo Удаление завершено!
            """)
        
        subprocess.Popen(['cmd.exe', '/c', uninstall_script], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Отправляем подтверждение перед завершением
        await update.message.reply_text("✅ Все файлы удаленного доступа удалены!")
        time.sleep(2)
        os._exit(0)
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка при удалении: {str(e)}",
            reply_markup=ReplyKeyboardMarkup(COMMAND_KEYBOARD, resize_keyboard=True)
        )
        return ConversationHandler.END

def main() -> None:
    logger.info(f"Скрипт запущен из: {os.path.abspath(__file__)}")
    
    try:
        # Отправляем уведомление о запуске
        asyncio.run(send_startup_notification())
        
        app = Application.builder().token(TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", start))
        app.add_handler(CommandHandler("screenshot", take_screenshot))
        app.add_handler(CommandHandler("systeminfo", system_info))
        
        # Обработчики процессов
        process_handler = ConversationHandler(
            entry_points=[CommandHandler('deleteprocess', delete_process_start)],
            states={
                WAITING_PROCESS_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_process)]
            },
            fallbacks=[]
        )
        
        # Обработчики клавиш
        key_handler = ConversationHandler(
            entry_points=[CommandHandler('presskey', press_key_start)],
            states={
                WAITING_KEY_PRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, press_key)]
            },
            fallbacks=[]
        )
        
        # Обработчики комбинаций
        hotkey_handler = ConversationHandler(
            entry_points=[CommandHandler('hotkey', hotkey_start)],
            states={
                WAITING_KEY_COMBINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, hotkey)]
            },
            fallbacks=[]
        )
        
        # Обработчик удаления
        delete_handler = ConversationHandler(
            entry_points=[CommandHandler('delete', delete_bot)],
            states={
                WAITING_DELETE_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete)]
            },
            fallbacks=[]
        )
        
        app.add_handler(process_handler)
        app.add_handler(key_handler)
        app.add_handler(hotkey_handler)
        app.add_handler(delete_handler)
        
        logger.info("Бот запускается...")
        app.run_polling()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
