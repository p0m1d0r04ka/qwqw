#!/data/data/com.termux/files/usr/bin/bash
# Скрипт для проверки обновлений userbot

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}┌─────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  Проверка обновлений Telegram UserBot│${NC}"
echo -e "${BLUE}└─────────────────────────────────────┘${NC}"

# Проверка работы в Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}Ошибка: Скрипт должен быть запущен в Termux!${NC}"
    exit 1
fi

# Путь к каталогу userbot
USERBOT_DIR="$HOME/userbot"

# Проверка наличия необходимых пакетов
if ! command -v pip &> /dev/null; then
    echo -e "${RED}Ошибка: pip не установлен!${NC}"
    echo -e "${YELLOW}Установка pip...${NC}"
    pkg install -y python-pip
fi

# Проверка каталога userbot
if [ ! -d "$USERBOT_DIR" ]; then
    echo -e "${RED}Ошибка: Каталог userbot не найден!${NC}"
    echo -e "${YELLOW}Создание каталога...${NC}"
    mkdir -p "$USERBOT_DIR"
fi

# Проверка наличия python-библиотек
echo -e "${YELLOW}Проверка Python-библиотек...${NC}"
REQUIRED_LIBRARIES=("telethon" "python-dotenv" "cryptg")
MISSING_LIBRARIES=()

for lib in "${REQUIRED_LIBRARIES[@]}"; do
    pip list | grep -i "$lib" &> /dev/null
    if [ $? -ne 0 ]; then
        MISSING_LIBRARIES+=("$lib")
    fi
done

if [ ${#MISSING_LIBRARIES[@]} -ne 0 ]; then
    echo -e "${YELLOW}Обнаружены отсутствующие библиотеки. Установка...${NC}"
    pip install "${MISSING_LIBRARIES[@]}"
    echo -e "${GREEN}Библиотеки успешно установлены!${NC}"
else
    echo -e "${GREEN}Все необходимые библиотеки установлены.${NC}"
fi

# Обновление pip
echo -e "${YELLOW}Обновление pip...${NC}"
pip install --upgrade pip &> /dev/null

# Проверка файлов userbot
echo -e "${YELLOW}Проверка файлов userbot...${NC}"
REQUIRED_FILES=("userbot.py" "log_management.py" "simple_start.py")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$USERBOT_DIR/$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    echo -e "${RED}Обнаружены отсутствующие файлы: ${MISSING_FILES[*]}${NC}"
    echo -e "${YELLOW}Требуется полная переустановка userbot.${NC}"
    echo -e "${YELLOW}Запустите:${NC}"
    echo -e "curl -sLo install.sh https://raw.githubusercontent.com/your-username/telegram-userbot/main/install_termux.sh && bash install.sh"
else
    echo -e "${GREEN}Все необходимые файлы присутствуют.${NC}"
fi

# Проверка скрипта запуска
if [ ! -f "$USERBOT_DIR/start_userbot.sh" ]; then
    echo -e "${YELLOW}Создание скрипта запуска...${NC}"
    cat > $USERBOT_DIR/start_userbot.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd $HOME/userbot
python log_management_main.py
EOF
    chmod +x $USERBOT_DIR/start_userbot.sh
    echo -e "${GREEN}Скрипт запуска создан!${NC}"
fi

# Проверка конфигурации
if [ ! -f "$USERBOT_DIR/.env" ]; then
    echo -e "${YELLOW}Файл конфигурации не найден!${NC}"
    echo -e "${YELLOW}Создание файла .env...${NC}"
    cat > $USERBOT_DIR/.env << 'EOF'
# Telegram API данные
API_ID=ваш_api_id
API_HASH=ваш_api_hash
EOF
    echo -e "${GREEN}Файл .env создан!${NC}"
    echo -e "${YELLOW}Отредактируйте файл $USERBOT_DIR/.env и укажите ваши API_ID и API_HASH${NC}"
else
    # Проверка содержимого .env
    grep -q "API_ID" $USERBOT_DIR/.env
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}В файле .env отсутствуют необходимые параметры!${NC}"
        echo -e "${YELLOW}Резервное копирование .env...${NC}"
        cp $USERBOT_DIR/.env $USERBOT_DIR/.env.backup
        
        # Добавление отсутствующих параметров
        echo -e "${YELLOW}Обновление файла .env...${NC}"
        echo -e "\n# Telegram API данные (добавлено автоматически)" >> $USERBOT_DIR/.env
        echo "API_ID=ваш_api_id" >> $USERBOT_DIR/.env
        echo "API_HASH=ваш_api_hash" >> $USERBOT_DIR/.env
        
        echo -e "${GREEN}Файл .env обновлен!${NC}"
        echo -e "${YELLOW}Отредактируйте файл $USERBOT_DIR/.env и укажите ваши API_ID и API_HASH${NC}"
    fi
fi

echo -e "${GREEN}┌──────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│  Проверка завершена успешно!             │${NC}"
echo -e "${GREEN}└──────────────────────────────────────────┘${NC}"

echo -e "${YELLOW}Для запуска UserBot выполните:${NC}"
echo -e "${BLUE}$USERBOT_DIR/start_userbot.sh${NC}"