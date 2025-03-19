#!/bin/bash
# Находим доступный интерпретатор Python
PYTHON_CMD="python3"

if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD="python"
    if ! command -v $PYTHON_CMD &> /dev/null; then
        echo "Ошибка: Python не найден"
        exit 1
    fi
fi

# Функция для обработки сессионного файла при запуске
check_session_file() {
    echo "Проверка сессионного файла..."
    
    # Проверяем наличие сессионного файла
    if [ -f "userbot.session" ]; then
        
        # Получаем информацию о размере файла
        size=$(stat -c%s "userbot.session" 2>/dev/null || stat -f%z "userbot.session" 2>/dev/null)
        
        # Если файл существует, но имеет нулевой размер или очень маленький размер (поврежден)
        if [ "$size" -lt 100 ]; then
            echo "Сессионный файл поврежден (размер: $size байт). Удаляем..."
            rm -f "userbot.session"
            echo "Сессионный файл удален. Будет создана новая сессия."
        else
            echo "Сессионный файл найден (размер: $size байт)."
            
            # Опционально: создаем бэкап сессии
            if [ ! -d "session_backups" ]; then
                mkdir -p "session_backups"
            fi
            
            # Создаем бэкап с временной меткой
            cp "userbot.session" "session_backups/userbot.session.backup.$(date +%Y%m%d_%H%M%S)"
            echo "Создан бэкап сессионного файла."
        fi
    else
        echo "Сессионный файл не найден. Будет создана новая сессия."
    fi
}

# Запускаем проверку и очистку сессии перед запуском
check_session_file

# Запускаем userbot с улучшенными параметрами
echo "Запуск Telegram UserBot..."
$PYTHON_CMD simple_run.py
