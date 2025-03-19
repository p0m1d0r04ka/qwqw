#!/data/data/com.termux/files/usr/bin/bash
# Скрипт для быстрого запуска Telegram UserBot в Termux

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}┌───────────────────────────────────┐${NC}"
echo -e "${BLUE}│  Запуск Telegram UserBot          │${NC}"
echo -e "${BLUE}└───────────────────────────────────┘${NC}"

# Проверка работы в Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}Ошибка: Скрипт должен быть запущен в Termux!${NC}"
    exit 1
fi

# Перейти в каталог скрипта
cd "$(dirname "$0")"

# Проверка наличия .env файла
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Файл .env не найден, создаем...${NC}"
    echo "# Telegram API данные" > .env
    echo "API_ID=ваш_api_id" >> .env
    echo "API_HASH=ваш_api_hash" >> .env
    echo -e "${GREEN}Файл .env создан.${NC}"
    echo -e "${YELLOW}Отредактируйте файл .env и укажите ваши данные от Telegram API.${NC}"
    exit 1
fi

# Проверка правильного заполнения .env
grep -q "ваш_api_id" .env
if [ $? -eq 0 ]; then
    echo -e "${RED}Ошибка: API_ID не настроен в файле .env${NC}"
    echo -e "${YELLOW}Отредактируйте файл .env и укажите правильные данные от Telegram API.${NC}"
    echo -e "nano .env"
    exit 1
fi

# Проверка наличия необходимых файлов
if [ ! -f "userbot.py" ] || [ ! -f "log_management.py" ]; then
    echo -e "${RED}Ошибка: необходимые файлы не найдены.${NC}"
    echo -e "${YELLOW}Запустите скрипт установки:${NC}"
    echo "curl -sLo install.sh https://raw.githubusercontent.com/your-username/telegram-userbot/main/install_termux.sh && bash install.sh"
    exit 1
fi

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python не установлен. Установка...${NC}"
    pkg install -y python
fi

# Проверка наличия необходимых библиотек
echo -e "${YELLOW}Проверка Python библиотек...${NC}"
pip list | grep -E "telethon|python-dotenv|cryptg" &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Установка необходимых библиотек...${NC}"
    pip install telethon python-dotenv cryptg
fi

# Запуск UserBot
echo -e "${GREEN}Запуск UserBot...${NC}"

# Проверка правильного запуска
if [ -f "log_management_main.py" ]; then
    python3 log_management_main.py
elif [ -f "simple_start.py" ]; then
    python3 simple_start.py
else
    python3 userbot.py
fi

# Запуск интерактивной оболочки в случае ошибки
if [ $? -ne 0 ]; then
    echo -e "${RED}UserBot завершился с ошибкой${NC}"
    echo -e "${YELLOW}Запуск диагностики...${NC}"
    echo -e "Проверка логов..."
    if [ -f "userbot.log" ]; then
        tail -n 20 userbot.log
    fi
    echo -e "${YELLOW}Для выхода нажмите Ctrl+C${NC}"
fi