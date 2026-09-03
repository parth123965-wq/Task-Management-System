from fastapi_mail import MessageSchema, MessageType
from app.core.config import setting
import logging
from aiosmtplib.errors import SMTPException
logger = logging.getLogger(__name__)
from app.core.email import EmailManager

class EmailService:
    @staticmethod
    async def send_otp_email(
        to_email: str,
        otp: int,
        purpose: str = "Verification"
    )->bool:
        client = EmailManager.mail_client
        if not client:
            logger.error("Attempted to send email before EmailManager was initialized.")
            return False
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
        try:
            await client.send_message(message=message,template_name="otp_verification.html")
            logger.info(f"OTP email sent successfully to {to_email}")
            return True
        except (SMTPException, TimeoutError) as e:
            logger.warning(f"Email failed to send to {to_email}: {e}")
            return False
    
    @staticmethod
    async def send_register_success_email(
        user_name: str,
        email: str,
    ) -> bool:
        client = EmailManager.mail_client
        if not client:
            logger.error("Attempted to send email before EmailManager was initialized.")
            return False
        message = MessageSchema(
            subject=f"Registration Successful - {setting.MAIL_FROM_NAME}",
            recipients=[email],
            template_body={
                "app_name":setting.MAIL_FROM_NAME,
                "user_name": user_name,
                "user_email": email
            },
            subtype=MessageType.html
        )
        try:
            await client.send_message(message=message,template_name="registration_success.html")
            logger.info(f"OTP email sent successfully to {email}")
            return True
        except (SMTPException, TimeoutError) as e:
            logger.warning(f"Email failed to send to {email}: {e}")
            return False