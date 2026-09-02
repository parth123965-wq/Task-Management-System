import logging
from fastapi_mail import ConnectionConfig, FastMail
from app.core.config import setting

logger = logging.getLogger(__name__)

class EmailManager:
    mail_client: FastMail|None = None
    @classmethod
    async def initilization_email_service(cls):
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
        cls.mail_client = FastMail(config=mail_config)
        logger.info("Email service initialized successfully.")
        
    @classmethod
    async def shutdown_email_service(cls):
        cls.mail_client = None
        logger.info("Email service stopped cleanly.")