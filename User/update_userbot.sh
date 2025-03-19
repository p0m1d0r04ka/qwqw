#!/bin/bash
# Скрипт для обновления Telegram UserBot

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}┌───────────────────────────────────┐${NC}"
echo -e "${BLUE}│  Обновление Telegram UserBot      │${NC}"
echo -e "${BLUE}└───────────────────────────────────┘${NC}"

# Проверка работы в Termux
if [ -d "/data/data/com.termux" ]; then
    TERMUX=true
    PREFIX="/data/data/com.termux/files/usr"
    USERBOT_DIR="$HOME/userbot"
else
    TERMUX=false
    PREFIX="/usr"
    USERBOT_DIR="$(pwd)"
fi

# Проверка наличия git
if ! command -v git &> /dev/null; then
    echo -e "${RED}Ошибка: Git не установлен!${NC}"
    if [ "$TERMUX" = true ]; then
        echo -e "${YELLOW}Установите Git с помощью:${NC}"
        echo -e "pkg install git"
    else
        echo -e "${YELLOW}Установите Git с помощью вашего менеджера пакетов.${NC}"
    fi
    exit 1
fi

# Проверка наличия pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Ошибка: pip не установлен!${NC}"
    if [ "$TERMUX" = true ]; then
        echo -e "${YELLOW}Установите pip с помощью:${NC}"
        echo -e "pkg install python-pip"
    else
        echo -e "${YELLOW}Установите pip с помощью вашего менеджера пакетов.${NC}"
    fi
    exit 1
fi

# Определение команды pip
if command -v pip3 &> /dev/null; then
    PIP="pip3"
else
    PIP="pip"
fi

# Проверка каталога userbot
if [ ! -d "$USERBOT_DIR" ]; then
    echo -e "${RED}Ошибка: Каталог userbot не найден!${NC}"
    echo -e "${YELLOW}Убедитесь, что вы запускаете скрипт из правильного каталога.${NC}"
    exit 1
fi

# Сохранение текущего файла .env
echo -e "${YELLOW}Сохранение текущей конфигурации...${NC}"
if [ -f "$USERBOT_DIR/.env" ]; then
    cp "$USERBOT_DIR/.env" "$USERBOT_DIR/.env.backup"
    echo -e "${GREEN}Файл .env сохранен как .env.backup${NC}"
fi

# Обновление зависимостей
echo -e "${YELLOW}Обновление Python-библиотек...${NC}"
$PIP install --upgrade telethon python-dotenv cryptg

# Обновление файлов userbot
echo -e "${YELLOW}Обновление файлов UserBot...${NC}"

# Проверка наличия директории .git
if [ -d "$USERBOT_DIR/.git" ]; then
    # Обновление из Git-репозитория
    echo -e "${BLUE}Обнаружен Git-репозиторий, обновление через Git...${NC}"
    cd "$USERBOT_DIR"
    
    # Сохранение текущих изменений
    git stash -u
    
    # Обновление из удаленного репозитория
    git pull origin main || git pull origin master
    
    # Восстановление изменений, если они были
    git stash pop 2>/dev/null || true
    
    echo -e "${GREEN}Обновление из Git-репозитория завершено!${NC}"
else
    # Загрузка актуальной версии скриптов
    echo -e "${BLUE}Git-репозиторий не найден, обновление через скачивание файлов...${NC}"
    
    # Создание временной директории
    TEMP_DIR=$(mktemp -d)
    
    # Здесь нужно добавить URL репозитория или архива с актуальной версией
    DOWNLOAD_URL="https://github.com/username/userbot-termux/archive/refs/heads/main.zip"
    
    # Скачивание архива
    if command -v wget &> /dev/null; then
        wget -q "$DOWNLOAD_URL" -O "$TEMP_DIR/userbot.zip"
    elif command -v curl &> /dev/null; then
        curl -s "$DOWNLOAD_URL" -o "$TEMP_DIR/userbot.zip"
    else
        echo -e "${RED}Ошибка: Не найдены программы для загрузки (wget или curl)!${NC}"
        if [ "$TERMUX" = true ]; then
            echo -e "${YELLOW}Установите wget с помощью:${NC}"
            echo -e "pkg install wget"
        fi
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    # Распаковка архива
    if command -v unzip &> /dev/null; then
        unzip -q "$TEMP_DIR/userbot.zip" -d "$TEMP_DIR"
        
        # Копирование файлов в директорию UserBot
        cp -r "$TEMP_DIR"/*/* "$USERBOT_DIR"
        
        echo -e "${GREEN}Обновление через скачивание файлов завершено!${NC}"
    else
        echo -e "${RED}Ошибка: Программа unzip не найдена!${NC}"
        if [ "$TERMUX" = true ]; then
            echo -e "${YELLOW}Установите unzip с помощью:${NC}"
            echo -e "pkg install unzip"
        fi
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    # Очистка временной директории
    rm -rf "$TEMP_DIR"
fi

# Создание файла requirements.txt, если он не существует
if [ ! -f "$USERBOT_DIR/requirements.txt" ]; then
    echo -e "${YELLOW}Создание файла requirements.txt...${NC}"
    cat > "$USERBOT_DIR/requirements.txt" << EOF
telethon>=1.28.5
python-dotenv>=0.21.1
cryptg>=0.4.0
psutil>=5.9.5
EOF
    echo -e "${GREEN}Файл requirements.txt создан!${NC}"
fi

# Установка зависимостей из requirements.txt
echo -e "${YELLOW}Установка зависимостей из requirements.txt...${NC}"
$PIP install --upgrade -r "$USERBOT_DIR/requirements.txt"

# Восстановление конфигурации
if [ -f "$USERBOT_DIR/.env.backup" ]; then
    cp "$USERBOT_DIR/.env.backup" "$USERBOT_DIR/.env"
    echo -e "${GREEN}Конфигурация восстановлена!${NC}"
fi

# Проверка прав на запуск
if [ -f "$USERBOT_DIR/start_userbot.sh" ]; then
    chmod +x "$USERBOT_DIR/start_userbot.sh"
fi

echo -e "${GREEN}┌─────────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│  Обновление UserBot успешно завершено!      │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────────┘${NC}"
echo -e ""
echo -e "${YELLOW}Вы можете запустить обновленный UserBot командой:${NC}"
echo -e "${BLUE}$USERBOT_DIR/start_userbot.sh${NC}"