from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from app.core.config import setting
import logging
from aiosmtplib.errors import SMTPException, SMTPServerDisconnected, SMTPTimeoutError
logger = logging.getLogger(__name__)
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
    )->bool:
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
            await fast_mail.send_message(message=message,template_name="otp_verification.html")
            logger.info(f"OTP email sent successfully to {to_email}")
            return True
        except (SMTPTimeoutError, TimeoutError):
            logger.error(f"SMTP Timeout: Mail server took too long to respond when sending OTP to {to_email}")
            return False

        except SMTPServerDisconnected:
            logger.error(f"SMTP Disconnect: Server dropped connection while sending OTP to {to_email}")
            return False

        except SMTPException as e:
            logger.error(f"SMTP Error for {to_email}: {str(e)}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error sending OTP to {to_email}: {str(e)}")
            return False