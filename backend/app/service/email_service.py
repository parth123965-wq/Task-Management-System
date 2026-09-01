from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from app.core.config import setting
from fastapi import BackgroundTasks

mail_config = ConnectionConfig(
    MAIL_USERNAME=setting.MAIL_USERNAME,
    MAIL_PASSWORD=setting.MAIL_PASSWORD,
    MAIL_PORT=setting.MAIL_PORT,
    MAIL_SERVER=setting.MAIL_SERVER,
    MAIL_STARTTLS=setting.MAIL_STARTTLS,
    MAIL_SSL_TLS=setting.MAIL_SSL_TSL,
    MAIL_FROM=setting.MAIL_FROM,
    MAIL_FROM_NAME=setting.MAIL_FROM_NAME,
    TEMPLATE_FOLDER=setting.TEMPLATE_FOLDER,
    USE_CREDENTIALS=setting.USE_CREDENTIALS,
    VALIDATE_CERTS=setting.VALIDATE_CERTS,
)

fast_mail = FastMail(config=mail_config)

class EmailService:
    @staticmethod
    async def send_otp_email(
        to_email: str,
        otp: int,
        purpose: str = "Varification"
    )->None:
        message = MessageSchema(
            subject=f"Your {purpose} Code: {otp}",
            recipients=[to_email],
            template_body={
                "app_name":setting.MAIL_FROM_NAME,
                "purpose":purpose,
                "otp": otp,
                "expire_minutes": setting.OTP_EXPIRY
            },
            subtype=MessageType.html
        )
        await fast_mail.send_message(message=message,template_name="otp_verification.html")