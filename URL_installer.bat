@echo off
setlocal

echo Загрузка RemoteAccessBot...
echo ---------------------------

set TEMP_DIR=%TEMP%\RemoteAccessBot
mkdir "%TEMP_DIR%" >nul 2>&1

echo Скачиваем файлы...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/ваш_аккаунт/ваш_репозиторий/main/remote_bot.py' -OutFile '%TEMP_DIR%\remote_bot.py'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/ваш_аккаунт/ваш_репозиторий/main/installer.bat' -OutFile '%TEMP_DIR%\installer.bat'"

echo Запускаем установщик...
cd /d "%TEMP_DIR%"
start /wait installer.bat

echo Очистка...
rd /s /q "%TEMP_DIR%"

echo Установка завершена!
pause