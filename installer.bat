@echo off
chcp 65001 >nul

set "TARGET_DIR=%ProgramFiles%\RemoteAccessBot"

echo Установка RemoteAccessBot...
echo ----------------------------

mkdir "%TARGET_DIR%" >nul 2>&1
copy "remote_bot.py" "%TARGET_DIR%\" >nul

where python >nul 2>nul
if errorlevel 1 (
    echo Установка Python...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe', 'python_installer.exe')"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_launcher=0
    del python_installer.exe
)

python -m pip install --upgrade pip >nul
pip install python-telegram-bot pyautogui pillow psutil >nul

set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_DIR%\RemoteAccessBot.lnk"

echo Создание ярлыка автозагрузки...
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath='pythonw.exe'; $s.Arguments='\"%TARGET_DIR%\remote_bot.py\"'; $s.WorkingDirectory='\"%TARGET_DIR%\"'; $s.WindowStyle=7; $s.Save()"

echo Запуск бота...
start "" /B pythonw "%TARGET_DIR%\remote_bot.py"

echo Установка завершена! Бот запущен.
echo Папка: %TARGET_DIR%
timeout /t 3 >nul
