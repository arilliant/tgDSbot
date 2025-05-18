@echo off
REM ===== Настройки =====
set "VENV_DIR=%~dp0.venv"
set "PY_SCRIPT=%~dp0bot.py"
set "LOG_DIR=%~dp0logs"
set "LOG_FILE=%LOG_DIR%\log.txt"

REM ===== Инициализация логов =====
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
echo [%date% %time%] === Запуск === > "%LOG_FILE%"

REM ===== Проверка виртуального окружения =====
if not exist "%VENV_DIR%" (
    echo [%date% %time%] ERROR: Виртуальное окружение не найдено в %VENV_DIR% >> "%LOG_FILE%"
    echo Виртуальное окружение не найдено!
    echo Создайте его командой: python -m venv "%VENV_DIR%"
    pause
    exit /b 1
)

REM ===== Запуск =====
call "%VENV_DIR%\Scripts\activate.bat" && (
    echo [%date% %time%] Виртуальное окружение активировано >> "%LOG_FILE%"
    echo [%date% %time%] Запуск скрипта: %PY_SCRIPT% >> "%LOG_FILE%"
    
    python "%PY_SCRIPT%" 2>&1 >> "%LOG_FILE%"
    
    if errorlevel 1 (
        echo [%date% %time%] ERROR: Скрипт завершился с кодом %errorlevel% >> "%LOG_FILE%"
        echo Ошибка! Подробности в логе: %LOG_FILE%
    ) else (
        echo [%date% %time%] Скрипт успешно завершен >> "%LOG_FILE%"
        echo Успешно! Лог: %LOG_FILE%
    )
)

pause