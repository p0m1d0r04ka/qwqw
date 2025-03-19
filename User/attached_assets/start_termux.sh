#!/bin/bash

# Цвета для красивого вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m' # Сброс цвета

echo -e "${YELLOW}${BOLD}======================================${RESET}"
echo -e "${GREEN}${BOLD}       Telegram Userbot для Termux     ${RESET}"
echo -e "${YELLOW}${BOLD}======================================${RESET}"
echo ""

# Функция проверки и установки зависимостей
check_dependencies() {
    # Проверка наличия Python
    if ! command -v python &> /dev/null; then
        echo -e "${RED}Python не установлен!${RESET}"
        echo -e "${YELLOW}Устанавливаем Python...${RESET}"
        pkg update
        pkg install -y python
    fi

    # Проверка и установка необходимых пакетов
    echo -e "${YELLOW}Проверка зависимостей...${RESET}"
    
    # Список зависимостей
    PACKAGES="telethon python-dotenv psutil aiohttp cryptg"
    MISSING=""
    
    # Проверка каждого пакета
    for package in $PACKAGES; do
        python -c "import $package" 2>/dev/null
        if [ $? -ne 0 ]; then
            MISSING="$MISSING $package"
        fi
    done
    
    # Установка отсутствующих пакетов
    if [ ! -z "$MISSING" ]; then
        echo -e "${YELLOW}Устанавливаем недостающие пакеты:${RESET} $MISSING"
        pip install $MISSING
    else
        echo -e "${GREEN}Все зависимости установлены${RESET}"
    fi
}

# Проверка и подготовка файлов
check_files() {
    # Проверка наличия скриптов запуска
    if [ ! -f "run_termux.py" ]; then
        echo -e "${RED}Файл run_termux.py не найден!${RESET}"
        echo -e "${YELLOW}Проверьте, правильно ли установлены файлы.${RESET}"
        exit 1
    fi
    
    if [ ! -f "userbot.py" ]; then
        echo -e "${RED}Файл userbot.py не найден!${RESET}"
        echo -e "${YELLOW}Проверьте, правильно ли установлены файлы.${RESET}"
        exit 1
    fi
    
    # Проверка наличия .env файла
    if [ ! -f ".env" ]; then
        echo -e "${RED}Файл .env не найден!${RESET}"
        echo -e "${YELLOW}Создаем шаблон .env файла...${RESET}"
        echo "API_ID=" > .env
        echo "API_HASH=" >> .env
        echo "PHONE=" >> .env
        
        echo -e "${RED}Пожалуйста, заполните файл .env вашими данными!${RESET}"
        echo -e "${YELLOW}Для этого выполните:${RESET}"
        echo -e "${GREEN}nano .env${RESET}"
        
        # Предлагаем заполнить файл сейчас
        read -p "Хотите заполнить данные сейчас? (y/n): " choice
        if [[ $choice == "y" || $choice == "Y" ]]; then
            nano .env
        else
            exit 1
        fi
    fi
    
    # Делаем скрипты исполняемыми
    chmod +x run_termux.py
    if [ -f "auth_termux.py" ]; then
        chmod +x auth_termux.py
    fi
}

# Проверка наличия сессии
check_session() {
    if [ ! -f "userbot.session" ]; then
        echo -e "${YELLOW}Сессия Telegram не найдена.${RESET}"
        
        if [ -f "auth_termux.py" ]; then
            echo -e "${GREEN}Запускаем процесс авторизации...${RESET}"
            python auth_termux.py
            
            # Проверяем, создана ли сессия после авторизации
            if [ ! -f "userbot.session" ]; then
                echo -e "${RED}Не удалось создать сессию. Повторите попытку позже.${RESET}"
                exit 1
            fi
        else
            echo -e "${RED}Файл auth_termux.py не найден!${RESET}"
            echo -e "${YELLOW}Необходимо авторизоваться вручную.${RESET}"
            exit 1
        fi
    fi
}

# Меню действий
show_menu() {
    echo -e "${YELLOW}${BOLD}Выберите действие:${RESET}"
    echo -e "${GREEN}1. Запустить userbot${RESET}"
    echo -e "${GREEN}2. Запустить в фоновом режиме (требуется screen)${RESET}"
    echo -e "${GREEN}3. Переавторизоваться${RESET}"
    echo -e "${GREEN}4. Показать логи${RESET}"
    echo -e "${GREEN}5. Показать информацию${RESET}"
    echo -e "${GREEN}0. Выход${RESET}"
    
    read -p "Ваш выбор: " choice
    
    case $choice in
        1)
            echo -e "${GREEN}Запускаем userbot...${RESET}"
            python run_termux.py
            ;;
        2)
            if ! command -v screen &> /dev/null; then
                echo -e "${YELLOW}Устанавливаем screen...${RESET}"
                pkg install -y screen
            fi
            
            # Проверяем, нет ли уже запущенной сессии
            screen -list | grep -q "userbot"
            if [ $? -eq 0 ]; then
                echo -e "${YELLOW}Userbot уже запущен в screen.${RESET}"
                echo -e "${GREEN}Вы можете подключиться к нему командой:${RESET} screen -r userbot"
                exit 0
            fi
            
            echo -e "${GREEN}Запускаем userbot в фоновом режиме...${RESET}"
            screen -dmS userbot python run_termux.py
            echo -e "${GREEN}Userbot запущен в фоновом режиме.${RESET}"
            echo -e "${YELLOW}Для подключения к сессии используйте команду:${RESET} screen -r userbot"
            echo -e "${YELLOW}Для отключения от сессии нажмите:${RESET} Ctrl+A, затем D"
            ;;
        3)
            if [ -f "auth_termux.py" ]; then
                # Удаляем существующую сессию
                if [ -f "userbot.session" ]; then
                    echo -e "${YELLOW}Удаляем существующую сессию...${RESET}"
                    rm userbot.session
                fi
                echo -e "${GREEN}Запускаем процесс авторизации...${RESET}"
                python auth_termux.py
            else
                echo -e "${RED}Файл auth_termux.py не найден!${RESET}"
            fi
            ;;
        4)
            echo -e "${GREEN}Показываем последние логи:${RESET}"
            if [ -f "userbot.log" ]; then
                tail -n 50 userbot.log
            else
                echo -e "${YELLOW}Файл логов не найден.${RESET}"
            fi
            ;;
        5)
            echo -e "${YELLOW}${BOLD}О программе:${RESET}"
            echo -e "${GREEN}Telegram Userbot - инструмент для автоматизации действий в Telegram.${RESET}"
            echo -e "${GREEN}Версия: 1.0${RESET}"
            echo -e "${GREEN}Команды бота: отправьте /help в любой чат${RESET}"
            echo -e "${GREEN}Полная документация: см. файл INSTALL_TERMUX.md${RESET}"
            ;;
        0)
            echo -e "${GREEN}Выход из программы.${RESET}"
            exit 0
            ;;
        *)
            echo -e "${RED}Неверный выбор!${RESET}"
            ;;
    esac
}

# Основная логика
check_dependencies
check_files
check_session
show_menu