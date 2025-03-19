#!/bin/bash
# Простой скрипт запуска Telegram UserBot в Termux

# ANSI цвета
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
RESET="\033[0m"
BOLD="\033[1m"

# Очистка экрана
clear

echo -e "${GREEN}${BOLD}===== Telegram UserBot для Termux =====${RESET}"
echo -e "${BLUE}Простая версия без веб-интерфейса${RESET}"
echo -e "${YELLOW}Время запуска: $(date +%H:%M:%S)${RESET}"
echo ""

# Проверка работы в Termux
if [ -d "/data/data/com.termux" ]; then
    echo -e "${GREEN}Обнаружена среда Termux${RESET}"
    TERMUX=1
else
    echo -e "${YELLOW}Запуск не в Termux окружении${RESET}"
    TERMUX=0
fi

# Проверка наличия Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}Python не установлен!${RESET}"
    if [ $TERMUX -eq 1 ]; then
        echo -e "${YELLOW}Установка Python...${RESET}"
        pkg install python -y
    else
        echo -e "${RED}Пожалуйста, установите Python и попробуйте снова${RESET}"
        exit 1
    fi
fi

# Проверка наличия pip
if ! command -v pip &> /dev/null; then
    echo -e "${RED}pip не установлен!${RESET}"
    if [ $TERMUX -eq 1 ]; then
        echo -e "${YELLOW}Установка pip...${RESET}"
        pkg install python-pip -y
    else
        echo -e "${RED}Пожалуйста, установите pip и попробуйте снова${RESET}"
        exit 1
    fi
fi

# Функция для установки зависимостей
install_dependencies() {
    echo -e "${BLUE}Установка зависимостей...${RESET}"
    pip install telethon python-dotenv cryptg
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Ошибка установки зависимостей!${RESET}"
        exit 1
    else
        echo -e "${GREEN}Зависимости установлены успешно${RESET}"
    fi
}

# Проверка наличия зависимостей
python -c "import telethon" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Библиотека telethon не установлена${RESET}"
    install_dependencies
fi

python -c "import dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Библиотека python-dotenv не установлена${RESET}"
    install_dependencies
fi

# Проверка наличия файла .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Файл .env не найден${RESET}"
    echo -e "${BLUE}Для использования userbot необходимо получить API ID и API HASH${RESET}"
    echo -e "${YELLOW}Получить их можно на сайте: https://my.telegram.org/apps${RESET}"
    
    read -p "Создать файл .env? (y/n): " CREATE_ENV
    if [[ $CREATE_ENV == "y" || $CREATE_ENV == "Y" ]]; then
        read -p "Введите API_ID: " API_ID
        read -p "Введите API_HASH: " API_HASH
        
        echo "API_ID=$API_ID" > .env
        echo "API_HASH=$API_HASH" >> .env
        
        echo -e "${GREEN}Файл .env создан${RESET}"
    else
        echo -e "${RED}Невозможно продолжить без файла .env${RESET}"
        exit 1
    fi
fi

# Запуск UserBot
echo -e "\n${GREEN}${BOLD}Запуск UserBot...${RESET}\n"

if [ $TERMUX -eq 1 ]; then
    # Оптимизации для Termux
    echo -e "${BLUE}Применение оптимизаций для Termux...${RESET}"
    python console_run.py --termux
else
    # Обычный запуск
    python console_run.py
fi

# Проверка результата запуска
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}UserBot завершил работу${RESET}"
else
    echo -e "\n${RED}UserBot завершил работу с ошибкой (код $?)${RESET}"
    
    # Запрос на перезапуск
    read -p "Перезапустить? (y/n): " RESTART
    if [[ $RESTART == "y" || $RESTART == "Y" ]]; then
        exec "$0"
    fi
fi