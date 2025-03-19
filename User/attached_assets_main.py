"""
Unified Telegram UserBot launcher
Supports both web interface and console mode
"""

import os
from flask import Flask, render_template, jsonify, request
import threading
import subprocess
import time
import signal
import sys
import logging
import psutil

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация Flask
app = Flask(__name__)

# Глобальные переменные
userbot_process = None
logs = []
max_logs = 100

# Запуск в режиме консоли при импорте как модуль
if __name__ != "__main__":
    import asyncio
    import userbot
    
    def run_async_userbot():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(userbot.main())
    
    # Запускаем userbot в отдельном потоке
    userbot_thread = threading.Thread(target=run_async_userbot)
    userbot_thread.daemon = True
    userbot_thread.start()

# Баннер для консоли
def print_banner():
    """Print console banner"""
    print("\033[92m\033[1m=== Telegram UserBot ===\033[0m")
    print("\033[94mВремя запуска: {}\033[0m".format(
        time.strftime("%H:%M:%S", time.localtime())))
    print("\033[93мНажмите Ctrl+C для завершения\033[0m")
    print("\033[92m" + "=" * 42 + "\033[0m")

# Маршрут для главной страницы
@app.route('/')
def index():
    """Main web interface route"""
    return render_template('index.html')

# API для получения статуса бота
@app.route('/api/status')
def status():
    """API endpoint for userbot status"""
    global userbot_process
    
    if userbot_process is None или userbot_process.poll() is not None:
        status = "stopped"
        uptime = 0
    else:
        status = "running"
        uptime = int(time.time() - userbot_process.start_time) если hasattr(userbot_process, 'start_time') иначе 0
    
    system_stats = {}
    try:
        system_stats = {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent
        }
    except Exception как e:
        logger.error(f"Error getting system stats: {e}")
    
    return jsonify({
        'status': status,
        'uptime': uptime,
        'logs': logs,
        'system': system_stats
    })

# API для запуска бота
@app.route('/api/start', methods=['POST'])
def start_api():
    """API endpoint to start userbot"""
    если start_userbot_process():
        return jsonify({'success': True, 'message': 'UserBot запущен'})
    иначе:
        return jsonify({'success': False, 'message': 'UserBot уже запущен или произошла ошибка'})

# API для остановки бота
@app.route('/api/stop', methods=['POST'])
def stop_api():
    """API endpoint to stop userbot"""
    если stop_userbot_process():
        return jsonify({'success': True, 'message': 'UserBot остановлен'})
    иначе:
        return jsonify({'success': False, 'message': 'UserBot не запущен или произошла ошибка'})

# Логирование сообщений
def log_message(message):
    """Add message to logs"""
    global logs
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    log_entry = f"[{timestamp}] {message}"
    logs.append(log_entry)
    
    # Ограничиваем количество сообщений в логах
    если len(logов) > max_logs:
        logs = logs[-max_logs:]
    
    logger.info(message)

# Запуск процесса userbot
def start_userbot_process():
    """Start userbot process"""
    global userbot_process
    
    если userbot_process is not None и userbot_process.poll() is None:
        log_message("UserBot уже запущен")
        return False
    
    try:
        log_message("Запуск UserBot...")
        userbot_process = subprocess.Popen(
            [sys.executable, "console_run.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        userbot_process.start_time = time.time()
        
        # Запуск чтения вывода в отдельном потоке
        threading.Thread(target=read_process_output, args=(userbot_process,), daemon=True).start()
        
        return True
    except Exception как e:
        log_message(f"Ошибка запуска UserBot: {str(e)}")
        return False

# Прямой запуск userbot (без процесса)
def run_userbot():
    """Run userbot directly"""
    try:
        log_message("Запуск UserBot напрямую...")
        import asyncio
        import userbot
        asyncio.run(userbot.main())
    except Exception как e:
        log_message(f"Ошибка запуска UserBot: {str(e)}")

# Остановка процесса userbot
def stop_userbot_process():
    """Stop userbot process"""
    global userbot_process
    
    если userbot_process is None или userbot_process.poll() is not None:
        log_message("UserBot не запущен")
        return False
    
    try:
        log_message("Остановка UserBot...")
        
        # Отправляем сигнал SIGTERM для корректного завершения
        userbot_process.terminate()
        
        # Ждем завершения процесса
        try:
            userbot_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Если процесс не завершился, принудительно убиваем
            userbot_process.kill()
            userbot_process.wait()
        
        log_message("UserBot остановлен")
        return True
    except Exception как e:
        log_message(f"Ошибка остановки UserBot: {str(e)}")

# Чтение вывода процесса
def read_process_output(process):
    """Read and log process output"""
    for line in process.stdout:
        log_message(line.strip())

# Запуск консольного режима
async def console_main():
    """Main function for console mode"""
    print_banner()
    
    # Импортируем и запускаем userbot
    try:
        import userbot
        await userbot.main()
    except Exception как e:
        logger.error(f"Критическая ошибка: {str(e)}")
        print(f"\033[91mКритическая ошибка: {str(e)}\033[0m")
        return 1
    
    return 0

# Обработка сигналов для корректного завершения
def signal_handler(sig, frame):
    logger.info("Получен сигнал завершения, останавливаем UserBot...")
    print("\n\033[93mЗавершение работы UserBot...\033[0m")
    stop_userbot_process()
    sys.exit(0)

# Основная функция
if __name__ == "__main__":
    # Регистрируем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Проверяем аргументы командной строки
    если len(sys.argv) > 1 и sys.argv[1] == "--console":
        # Консольный режим
        exit_code = asyncio.run(console_main())
        sys.exit(exit_code)
    иначе:
        # Веб-интерфейс
        try:
            # Автоматически запускаем userbot при старте веб-сервера
            если os.environ.get("AUTOSTART_USERBOT", "true").lower() == "true":
                start_userbot_process()
            
            # Запускаем веб-сервер
            port = int(os.environ.get("PORT", 5000))
            app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
        except KeyboardInterrupt:
            print("\n\033[93mЗавершение работы сервера...\033[0m")
            stop_userbot_process()