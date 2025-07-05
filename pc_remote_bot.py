import os
import shutil
import sys
import logging
import subprocess
import time
import json
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
import pygetwindow as gw
import ctypes

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
WAITING_PROCESS_NAME, WAITING_KEY_PRESS, WAITING_KEY_COMBINATION, WAITING_DELETE_CONFIRM = range(4)

# Функция для перемещения скрипта
def move_to_pppython():
    target_dir = r"C:\pppython"
    current_file = os.path.abspath(__file__)
    target_file = os.path.join(target_dir, os.path.basename(current_file))
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    if os.path.dirname(current_file).lower() == target_dir.lower():
        return False
    
    shutil.copy(current_file, target_file)
    logger.info(f"Файл скопирован в: {target_file}")
    
    subprocess.Popen([sys.executable, target_file])
    return True

if move_to_pppython():
    logger.info("Скрипт перемещен. Запускаю новую копию...")
    sys.exit(0)

# Проверка прав администратора
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Специальные обработчики для системных комбинаций
def execute_special_hotkey(combination: str):
    combination = combination.lower()
    
    # Блокировка компьютера
    if combination == "ctrl+alt+delete" or combination == "ctrl+alt+del":
        ctypes.windll.user32.LockWorkStation()
        return "Компьютер заблокирован"
    
    # Диспетчер задач
    elif combination == "ctrl+shift+esc":
        os.system("taskmgr")
        return "Открыт диспетчер задач"
    
    # Переключение окон
    elif combination == "alt+tab":
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        pyautogui.keyUp('alt')
        return "Выполнено переключение окон"
    
    # Рабочий стол
    elif combination == "win+d":
        pyautogui.hotkey('win', 'd')
        return "Показан рабочий стол"
    
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return
    
    admin_status = "✅ Есть права администратора" if is_admin() else "⚠️ Нет прав администратора (некоторые функции могут не работать)"
    
    help_text = f"""
🤖 Бот для удаленного доступа к ПК
{admin_status}

Доступные команды:
/screenshot - Скриншот экрана
/deleteprocess - Закрыть процесс
/presskey - Нажать клавишу
/hotkey - Комбинация клавиш
/delete - Полностью удалить бота
/help - Справка

🔥 Поддерживаемые комбинации:
ctrl+alt+delete - Блокировка компьютера
ctrl+shift+esc - Диспетчер задач
alt+tab - Переключение окон
win+d - Показать рабочий стол
win+l - Заблокировать компьютер
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
                try:
                    proc.kill()
                    killed.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
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
        # Специальная обработка для Enter
        if key.lower() == 'enter':
            key = 'enter'
        pyautogui.press(key)
        await update.message.reply_text(f"✅ Нажата клавиша: {key}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}\nПопробуйте другое название клавиши.")
    
    return ConversationHandler.END

async def hotkey_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен.")
        return ConversationHandler.END
    
    # Сразу предлагаем популярные комбинации
    buttons = [
        ["Ctrl+Alt+Delete", "Ctrl+Shift+Esc"],
        ["Alt+Tab", "Win+D"],
        ["Win+L", "Custom"]
    ]
    reply_markup = {
        "keyboard": buttons,
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    
    await update.message.reply_text(
        "⌨️ Выберите комбинацию или введите свою (через '+'):",
        reply_markup=json.dumps(reply_markup)
    )
    return WAITING_KEY_COMBINATION

async def hotkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    combination = update.message.text.strip()
    
    try:
        # Проверяем специальные комбинации
        special_result = execute_special_hotkey(combination)
        if special_result:
            await update.message.reply_text(f"✅ {special_result}")
            return ConversationHandler.END
        
        # Обработка кастомных комбинаций
        keys = combination.split('+')
        pyautogui.hotkey(*keys)
        await update.message.reply_text(f"✅ Нажата комбинация: {combination}")
    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        if "is not a valid key" in str(e):
            error_msg += "\nℹ️ Проверьте правильность названий клавиш"
        if not is_admin():
            error_msg += "\n⚠️ Требуются права администратора для некоторых комбинаций"
        
        await update.message.reply_text(error_msg)
    
    # Сбрасываем клавиатуру
    await update.message.reply_text(
        "Готово!",
        reply_markup=json.dumps({"remove_keyboard": True})
    )
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
        
        with open(uninstall_script, "w", encoding='utf-8') as f:
            f.write(f"""
@echo off
chcp 65001 > nul
echo Удаление бота удаленного доступа...
timeout /t 3 /nobreak >nul

taskkill /f /im pythonw.exe >nul 2>&1
rd /s /q "{current_dir}" >nul 2>&1

del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\PC_Remote_Bot.lnk" >nul 2>&1
del "%USERPROFILE%\\Desktop\\Telegram PC Bot.lnk" >nul 2>&1

echo Удаление завершено!
timeout /t 2 /nobreak >nul
del "%~f0"
""")
        
        subprocess.Popen(
            ['cmd.exe', '/c', uninstall_script],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        await update.message.reply_text("✅ Все файлы удаленного доступа будут удалены через 5 секунд...")
        time.sleep(5)
        os._exit(0)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при удалении: {str(e)}")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Операция отменена")
    return ConversationHandler.END

def main() -> None:
    logger.info(f"Бот запущен из: {os.path.abspath(__file__)}")
    
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Основные команды без состояний
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", start))
        app.add_handler(CommandHandler("screenshot", take_screenshot))
        
        # Обработчики с состояниями
        conv_handler_process = ConversationHandler(
            entry_points=[CommandHandler('deleteprocess', delete_process_start)],
            states={
                WAITING_PROCESS_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_process)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_user=True
        )
        
        conv_handler_presskey = ConversationHandler(
            entry_points=[CommandHandler('presskey', press_key_start)],
            states={
                WAITING_KEY_PRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, press_key)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_user=True
        )
        
        conv_handler_hotkey = ConversationHandler(
            entry_points=[CommandHandler('hotkey', hotkey_start)],
            states={
                WAITING_KEY_COMBINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, hotkey)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_user=True
        )
        
        conv_handler_delete = ConversationHandler(
            entry_points=[CommandHandler('delete', delete_bot)],
            states={
                WAITING_DELETE_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_user=True
        )
        
        # Регистрация обработчиков
        app.add_handler(conv_handler_process)
        app.add_handler(conv_handler_presskey)
        app.add_handler(conv_handler_hotkey)
        app.add_handler(conv_handler_delete)
        
        logger.info("Обработчики команд успешно зарегистрированы")
        logger.info("Бот запускается...")
        app.run_polling()
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
