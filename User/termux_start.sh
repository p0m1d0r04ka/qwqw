#!/data/data/com.termux/files/usr/bin/bash
# Скрипт для быстрого запуска UserBot в Termux

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}┌───────────────────────────────────┐${NC}"
echo -e "${BLUE}│  Запуск Telegram UserBot в Termux │${NC}"
echo -e "${BLUE}└───────────────────────────────────┘${NC}"

# Перейти в каталог скрипта
cd "$(dirname "$0")"

# Проверить наличие .env файла
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Файл .env не найден, создаем...${NC}"
    echo "# Telegram API данные" > .env
    echo "API_ID=ваш_api_id" >> .env
    echo "API_HASH=ваш_api_hash" >> .env
    echo -e "${GREEN}Файл .env создан.${NC}"
    echo -e "${YELLOW}Отредактируйте файл .env и укажите ваши данные от Telegram API.${NC}"
    echo -e "${YELLOW}Для этого выполните:${NC}"
    echo -e "nano .env"
    exit 1
fi

# Проверить наличие Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python не установлен. Установка...${NC}"
    pkg install -y python
fi

# Проверить наличие необходимых библиотек
echo -e "${YELLOW}Проверка Python библиотек...${NC}"
pip list | grep -E "telethon|python-dotenv|cryptg" &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Установка необходимых библиотек...${NC}"
    pip install telethon python-dotenv cryptg
fi

# Запуск UserBot
echo -e "${GREEN}Запуск UserBot...${NC}"
python3 simple_start.py

# Запуск интерактивной оболочки в случае ошибки
if [ $? -ne 0 ]; then
    echo -e "${RED}UserBot завершился с ошибкой${NC}"
    echo -e "${YELLOW}Запуск интерактивной оболочки для диагностики...${NC}"
    echo -e "Для выхода введите 'exit'${NC}"
    python3 -c "import code; code.interact(local=locals())"
fi