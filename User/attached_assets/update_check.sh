#!/bin/bash
# Скрипт для проверки и обновления Telegram UserBot
# Запускается перед запуском основного бота

# ANSI цвета
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
RESET="\033[0m"
BOLD="\033[1m"

echo -e "${BLUE}${BOLD}=== Проверка обновлений Telegram UserBot ===${RESET}"

# Проверка запуска в Termux
if [ -d "/data/data/com.termux" ]; then
    echo -e "${GREEN}Среда Termux обнаружена${RESET}"
    TERMUX=1
else
    TERMUX=0
fi

# Проверка наличия git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Git не установлен. Установка...${RESET}"
    if [ $TERMUX -eq 1 ]; then
        pkg install git -y
    else
        echo -e "${RED}Установите git вручную и запустите скрипт снова${RESET}"
        exit 1
    fi
fi

# Проверка наличия Python
if ! command -v python &> /dev/null; then
    echo -e "${YELLOW}Python не установлен. Установка...${RESET}"
    if [ $TERMUX -eq 1 ]; then
        pkg install python -y
    else
        echo -e "${RED}Установите Python вручную и запустите скрипт снова${RESET}"
        exit 1
    fi
fi

# Проверка, находимся ли мы в репозитории git
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Не обнаружен репозиторий Git.${RESET}"
    echo -e "${BLUE}Репозиторий Git необходим для проверки обновлений.${RESET}"
    echo "Пропускаем проверку обновлений..."
else
    # Проверка обновлений
    echo -e "${BLUE}Проверка наличия обновлений...${RESET}"
    git fetch origin
    
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    
    if [ $LOCAL = $REMOTE ]; then
        echo -e "${GREEN}У вас последняя версия UserBot${RESET}"
    else
        echo -e "${YELLOW}Доступна новая версия!${RESET}"
        read -p "Установить обновления? (y/n): " UPDATE
        
        if [[ $UPDATE == "y" || $UPDATE == "Y" ]]; then
            echo -e "${BLUE}Обновление...${RESET}"
            git pull
            
            # Проверка результата обновления
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}Обновление успешно установлено${RESET}"
                
                # Обновление зависимостей
                echo -e "${BLUE}Проверка зависимостей...${RESET}"
                pip install -r requirements.txt
            else
                echo -e "${RED}Ошибка при обновлении.${RESET}"
                echo -e "${YELLOW}Возможно, у вас есть локальные изменения.${RESET}"
            fi
        else
            echo -e "${YELLOW}Обновление пропущено.${RESET}"
        fi
    fi
fi

# Проверка зависимостей
echo -e "${BLUE}Проверка необходимых библиотек Python...${RESET}"

# Проверка наличия telethon
python -c "import telethon" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Telethon не установлен. Установка...${RESET}"
    pip install telethon
fi

# Проверка наличия python-dotenv
python -c "import dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}python-dotenv не установлен. Установка...${RESET}"
    pip install python-dotenv
fi

# Проверка наличия cryptg для ускорения
python -c "import cryptg" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}cryptg не установлен. Установка...${RESET}"
    pip install cryptg
fi

echo -e "${GREEN}Все необходимые компоненты установлены${RESET}"
echo -e "${BLUE}Можно запускать UserBot (./simple_start.sh или python simple_run.py)${RESET}"