@echo off
chcp 1251 >nul

echo ��������� RemoteAccessBot...
echo ----------------------------

set TARGET_DIR=%ProgramFiles%\RemoteAccessBot

echo ������� ������� �����: %TARGET_DIR%
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo �������� �����...
copy "%~dp0remote_bot.py" "%TARGET_DIR%\" >nul

echo ��������� Python...
where python >nul 2>nul
if errorlevel 1 (
    echo Python �� ������, �������������...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe', 'python_installer.exe')"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_launcher=0
    del python_installer.exe
)

echo ��������� pip...
python -m pip install --upgrade pip >nul

echo ������������� �����������...
cd /d "%TARGET_DIR%"
pip install python-telegram-bot pyautogui pillow psutil >nul

echo ������� ����� ������������...
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_PATH=%STARTUP_DIR%\RemoteAccessBot.lnk

powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath='pythonw.exe'; $s.Arguments='\"%TARGET_DIR%\remote_bot.py\"'; $s.WorkingDirectory='\"%TARGET_DIR%\"'; $s.WindowStyle=7; $s.Save()"

echo ��������� ����...
start "" /B pythonw "%TARGET_DIR%\remote_bot.py"

echo ��������� ���������!
echo ��� ������� � ����� ������������� ����������� ��� ����� � �������
echo ����� � �����: %TARGET_DIR%
pause