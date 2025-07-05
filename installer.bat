@echo off
chcp 1251 >nul

echo Установка RemoteAccessBot...
echo ----------------------------

set TARGET_DIR=%ProgramFiles%\RemoteAccessBot

echo Создаем целевую папку: %TARGET_DIR%
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo Копируем файлы...
copy "%~dp0remote_bot.py" "%TARGET_DIR%\" >nul

echo Проверяем Python...
where python >nul 2>nul
if errorlevel 1 (
    echo Python не найден, устанавливаем...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe', 'python_installer.exe')"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_launcher=0
    del python_installer.exe
)

echo Обновляем pip...
python -m pip install --upgrade pip >nul

echo Устанавливаем зависимости...
cd /d "%TARGET_DIR%"
pip install python-telegram-bot pyautogui pillow psutil >nul

echo Создаем ярлык автозагрузки...
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_PATH=%STARTUP_DIR%\RemoteAccessBot.lnk

powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath='pythonw.exe'; $s.Arguments='\"%TARGET_DIR%\remote_bot.py\"'; $s.WorkingDirectory='\"%TARGET_DIR%\"'; $s.WindowStyle=7; $s.Save()"

echo Запускаем бота...
start "" /B pythonw "%TARGET_DIR%\remote_bot.py"

echo Установка завершена!
echo Бот запущен и будет автоматически запускаться при входе в систему
echo Папка с ботом: %TARGET_DIR%
pause