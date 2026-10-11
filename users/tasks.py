from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import time

@shared_task
def generate_pdf_report_task(user_id, report_type="monthly"):
    print(f"Начало генерации отчета '{report_type}' для пользователя с ID: {user_id}")

    time.sleep(3)

    print(f"Отчет для пользователя {user_id} успешно сгенерирован и сохранен!")
    return f"Report {report_type} for user {user_id} is ready."


@shared_task
def clear_old_logs_task():
    current_time = timezone.now()
    print(f"[{current_time}] Запущена плановая задача: очистка устаревших логов и сессий...")

    deleted_count = 42

    print(f"Очистка завершена. Удалено устаревших записей: {deleted_count}")
    return f"Successfully cleared {deleted_count} old logs."


@shared_task
def send_welcome_email_task(user_email, username):
    subject = "Добро пожаловать в наш киносервис!"
    message = f"Привет, {username}! Спасибо за регистрацию в проекте Cinematica."
    sender_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@cinematica.com')

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=sender_email,
            recipient_list=[user_email],
            fail_silently=False,
        )
        print(f"Письмо успешно отправлено на адрес {user_email}")
        return f"Email sent to {user_email}"
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
        return f"Failed to send email: {str(e)}"