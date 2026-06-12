from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Self
from pydantic import (
    EmailStr,
    computed_field,
    model_validator,
)
import secrets
import warnings

class Settings(BaseSettings):
    # load everything from .env
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    # Runs only when there is no secret key in .env
    SECRET_KEY: str = secrets.token_urlsafe(32)

    SQLITE_URL: str
    SQLITE_TEST_URL: str

    TEST_USER_EMAIL: EmailStr = "test@example.com"
    INITIAL_SUPERUSER: EmailStr
    INITIAL_SUPERUSER_PASSWORD: str

    """ def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            warnings.warn(message, stacklevel=1)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)

        return self """
    
settings = Settings()