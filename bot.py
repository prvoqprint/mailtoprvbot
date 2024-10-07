import os
import smtplib
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Получение настроек из переменных окружения
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Функция для отправки файлов на почту
def send_email(file_path, file_name):
    try:
        # Настраиваем сообщение
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = 'Файл от Telegram бота'

        # Прикрепляем файл
        with open(file_path, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={file_name}')
            msg.attach(part)

        # Отправка почты через SMTP сервер
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
        server.quit()

        print(f"Файл {file_name} успешно отправлен на {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"Ошибка при отправке почты: {e}")

# Обработчик команды /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправьте мне файл, и я перешлю его на указанный email.')

# Обработчик файлов
def handle_file(update: Update, context: CallbackContext) -> None:
    # Получаем файл из сообщения
    file = update.message.document
    if file:
        file_name = file.file_name
        file_id = file.file_id
        new_file = context.bot.get_file(file_id)

        # Сохраняем файл временно
        file_path = os.path.join("/tmp", file_name)
        new_file.download(file_path)

        # Отправляем файл на почту
        send_email(file_path, file_name)

        # Удаляем временный файл
        os.remove(file_path)

        # Уведомляем пользователя
        update.message.reply_text(f"Файл {file_name} успешно отправлен на {RECIPIENT_EMAIL}")

# Главная функция для запуска бота
def main() -> None:
    # Инициализация бота
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    # Получение диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Команда /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Обработчик файлов
    dispatcher.add_handler(MessageHandler(Filters.document, handle_file))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
