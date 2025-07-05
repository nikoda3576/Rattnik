import os
import sys
import logging
import subprocess
import time
from telegram import Update
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
/delete - Полностью удалить бота
/help - Справка
"""
    await update.message.reply_text(help_text)

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
            caption="📸 Скриншот экрана"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def delete_process_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return ConversationHandler.END
    
    await update.message.reply_text("✏️ Введите имя процесса для закрытия (например: notepad.exe):")
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
            await update.message.reply_text(f"✅ Успешно закрыто процессов {len(killed)}: {', '.join(killed)}")
        else:
            await update.message.reply_text(f"⚠️ Процессы с именем '{process_name}' не найдены")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при закрытии процесса: {str(e)}")
    
    return ConversationHandler.END

async def press_key_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return ConversationHandler.END
    
    await update.message.reply_text("⌨️ Введите клавишу для нажатия (например: f, Enter, Escape, Space):")
    return WAITING_KEY_PRESS

async def press_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    key = update.message.text.strip()
    
    try:
        pyautogui.press(key)
        await update.message.reply_text(f"✅ Нажата клавиша: {key}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}\nПопробуйте другое название клавиши.")
    
    return ConversationHandler.END

async def hotkey_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return ConversationHandler.END
    
    await update.message.reply_text("⌨️ Введите комбинацию клавиш через '+' (например: ctrl+alt+delete, shift+a):")
    return WAITING_KEY_COMBINATION

async def hotkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    combination = update.message.text.strip()
    
    try:
        keys = combination.split('+')
        pyautogui.hotkey(*keys)
        await update.message.reply_text(f"✅ Нажата комбинация: {combination}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}\nПроверьте правильность формата.")
    
    return ConversationHandler.END

async def delete_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "⚠️ ВНИМАНИЕ! Это удалит все файлы бота и записи автозагрузки.\n"
        "Отправьте 'ПОДТВЕРЖДАЮ' для удаления:"
    )
    return WAITING_DELETE_CONFIRM

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.strip().upper() != "ПОДТВЕРЖДАЮ":
        await update.message.reply_text("❌ Удаление отменено")
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
        await update.message.reply_text("✅ Все файлы удаленного доступа удалены!")
        time.sleep(2)
        os._exit(0)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при удалении: {str(e)}")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Операция отменена")
    return ConversationHandler.END

def main() -> None:
    logger.info(f"Скрипт запущен из: {os.path.abspath(__file__)}")
    
    try:
        app = Application.builder().token(TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", start))
        app.add_handler(CommandHandler("screenshot", take_screenshot))
        
        process_handler = ConversationHandler(
            entry_points=[CommandHandler('deleteprocess', delete_process_start)],
            states={
                WAITING_PROCESS_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_process)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        
        key_handler = ConversationHandler(
            entry_points=[CommandHandler('presskey', press_key_start)],
            states={
                WAITING_KEY_PRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, press_key)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        
        hotkey_handler = ConversationHandler(
            entry_points=[CommandHandler('hotkey', hotkey_start)],
            states={
                WAITING_KEY_COMBINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, hotkey)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        
        delete_handler = ConversationHandler(
            entry_points=[CommandHandler('delete', delete_bot)],
            states={
                WAITING_DELETE_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
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
