from os import getenv

from celery import shared_task
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()


@shared_task
def send_sms(to, code):
    client = Client(getenv('TWILIO_SID'), getenv('TWILIO_TOKEN'))

    try:
        message = client.messages.create(
            body=f"Your code: {code} 5 minutes valid!",
            from_=getenv('TWILIO_PHONE_NUMBER'),
            to=to,
        )
        print(f"SMS muvaffaqiyatli jo‘natildi! Message SID: {message.sid}")
        return True
    except Exception as e:
        print(f"SMS jo‘natishda xatolik: {str(e)}")
        return False