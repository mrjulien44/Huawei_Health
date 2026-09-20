# import secrets,voluptuous as vol
# from homeassistant import config_entries
# from homeassistant.const import CONF_CLIENT_ID,CONF_CLIENT_SECRET,CONF_NAME
# from homeassistant.helpers.aiohttp_client import async_get_clientsession
# from .api import HuaweiHealthClient
# from .const import *
# from .exceptions import HuaweiHealthError
# import logging
# _LOGGER = logging.getLogger(__name__)

# class HuaweiHealthConfigFlow(config_entries.ConfigFlow,domain=DOMAIN):
#  VERSION=1
#  def __init__(self):self._credentials={};self._state='';self._auth_url=''
#  async def async_step_user(self,user_input=None):
#   if user_input:
#    self._credentials=dict(user_input);self._state=secrets.token_urlsafe(24);c=HuaweiHealthClient(async_get_clientsession(self.hass),user_input[CONF_CLIENT_ID],user_input[CONF_CLIENT_SECRET],user_input[CONF_REDIRECT_URI],REGION_API_BASE[user_input[CONF_REGION]])
#    self._auth_url=c.authorization_url(['openid',ACTIVITY_SCOPE,SLEEP_SCOPE],self._state);return await self.async_step_authorize()
#   return self.async_show_form(step_id='user',data_schema=vol.Schema({vol.Required(CONF_NAME,default=DEFAULT_NAME):str,vol.Required(CONF_CLIENT_ID):str,vol.Required(CONF_CLIENT_SECRET):str,vol.Required(CONF_REDIRECT_URI):str,vol.Required(CONF_REGION,default=DEFAULT_REGION):vol.In(REGION_API_BASE)}))
#  async def async_step_authorize(self,user_input=None):
#   errors={}
#   if user_input:
#    c=HuaweiHealthClient(async_get_clientsession(self.hass),self._credentials[CONF_CLIENT_ID],self._credentials[CONF_CLIENT_SECRET],self._credentials[CONF_REDIRECT_URI],REGION_API_BASE[self._credentials[CONF_REGION]])
#    try:t=await c.exchange_code(user_input['authorization_code'])
#    except HuaweiHealthError:errors['base']='cannot_connect'
#    else:
#     await self.async_set_unique_id(f"huawei_health_{self._credentials[CONF_CLIENT_ID]}");self._abort_if_unique_id_configured();d={**self._credentials,CONF_ACCESS_TOKEN:t.get('access_token'),CONF_REFRESH_TOKEN:t.get('refresh_token'),CONF_EXPIRES_AT:t.get('expires_in')};return self.async_create_entry(title=self._credentials[CONF_NAME],data=d,options={CONF_ENABLE_ACTIVITIES:True,CONF_ENABLE_SLEEP:True,CONF_ENABLE_NAPS:True,CONF_HISTORY_DAYS:30})
#   return self.async_show_form(step_id='authorize',description_placeholders={'authorization_url':self._auth_url},data_schema=vol.Schema({vol.Required('authorization_code'):str}),errors=errors)
#  @staticmethod
#  def async_get_options_flow(entry):return HuaweiHealthOptionsFlow(entry)
# class HuaweiHealthOptionsFlow(config_entries.OptionsFlow):
#  def __init__(self,e):self.e=e
#  async def async_step_init(self,user_input=None):
#   if user_input is not None:return self.async_create_entry(title='',data=user_input)
#   o=self.e.options;return self.async_show_form(step_id='init',data_schema=vol.Schema({vol.Required(CONF_ENABLE_ACTIVITIES,default=o.get(CONF_ENABLE_ACTIVITIES,True)):bool,vol.Required(CONF_ENABLE_SLEEP,default=o.get(CONF_ENABLE_SLEEP,True)):bool,vol.Required(CONF_ENABLE_NAPS,default=o.get(CONF_ENABLE_NAPS,True)):bool,vol.Required(CONF_HISTORY_DAYS,default=o.get(CONF_HISTORY_DAYS,30)):vol.All(int,vol.Range(min=1,max=365))}))

"""Config flow for Huawei Health."""

from __future__ import annotations

import logging
import secrets

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_NAME,
)

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HuaweiHealthClient
from .const import (
    ACTIVITY_SCOPE,
    CONF_ACCESS_TOKEN,
    CONF_ENABLE_ACTIVITIES,
    CONF_ENABLE_NAPS,
    CONF_ENABLE_SLEEP,
    CONF_EXPIRES_AT,
    CONF_HISTORY_DAYS,
    CONF_REDIRECT_URI,
    CONF_REFRESH_TOKEN,
    CONF_REGION,
    DEFAULT_HISTORY_DAYS,
    DEFAULT_NAME,
    DEFAULT_REGION,
    DOMAIN,
    REGION_API_BASE,
    SLEEP_SCOPE,
)
from .exceptions import HuaweiHealthError

_LOGGER = logging.getLogger(__name__)


class HuaweiHealthConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a Huawei Health config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._credentials: dict = {}
        self._state: str = ""
        self._auth_url: str = ""

    async def async_step_user(self, user_input=None):
        """Initial step."""

        if user_input is not None:
            self._credentials = dict(user_input)

            self._state = secrets.token_urlsafe(24)

            client = HuaweiHealthClient(
                async_get_clientsession(self.hass),
                user_input[CONF_CLIENT_ID],
                user_input[CONF_CLIENT_SECRET],
                user_input[CONF_REDIRECT_URI],
                REGION_API_BASE[user_input[CONF_REGION]],
            )

            self._auth_url = client.authorization_url(
                [
                    "openid",
                    ACTIVITY_SCOPE,
                    SLEEP_SCOPE,
                ],
                self._state,
            )

            _LOGGER.debug(
                "OAuth authorization URL generated for client_id=%s",
                user_input[CONF_CLIENT_ID],
            )

            return await self.async_step_authorize()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=DEFAULT_NAME,
                    ): str,
                    vol.Required(CONF_CLIENT_ID): str,
                    vol.Required(CONF_CLIENT_SECRET): str,
                    vol.Required(CONF_REDIRECT_URI): str,
                    vol.Required(
                        CONF_REGION,
                        default=DEFAULT_REGION,
                    ): vol.In(REGION_API_BASE),
                }
            ),
        )

    async def async_step_authorize(self, user_input=None):
        """Handle authorization code exchange."""

        errors = {}

        if user_input is not None:
            client = HuaweiHealthClient(
                async_get_clientsession(self.hass),
                self._credentials[CONF_CLIENT_ID],
                self._credentials[CONF_CLIENT_SECRET],
                self._credentials[CONF_REDIRECT_URI],
                REGION_API_BASE[
                    self._credentials[CONF_REGION]
                ],
            )

            try:
                token_data = await client.exchange_code(
                    user_input["authorization_code"]
                )

                access_token = token_data.get("access_token")

                if not access_token:
                    raise HuaweiHealthError(
                        "Missing access_token in OAuth response"
                    )

            except HuaweiHealthError as err:
                _LOGGER.exception(
                    "Huawei OAuth authorization failed: %s",
                    err,
                )

                errors["base"] = "cannot_connect"

            else:
                await self.async_set_unique_id(
                    f"huawei_health_{self._credentials[CONF_CLIENT_ID]}"
                )
                self._abort_if_unique_id_configured()

                entry_data = {
                    **self._credentials,
                    CONF_ACCESS_TOKEN: access_token,
                    CONF_REFRESH_TOKEN: token_data.get(
                        "refresh_token"
                    ),
                    CONF_EXPIRES_AT: token_data.get(
                        "expires_at",
                        token_data.get("expires_in"),
                    ),
                }

                _LOGGER.info(
                    "Huawei Health account successfully linked"
                )

                return self.async_create_entry(
                    title=self._credentials[CONF_NAME],
                    data=entry_data,
                    options={
                        CONF_ENABLE_ACTIVITIES: True,
                        CONF_ENABLE_SLEEP: True,
                        CONF_ENABLE_NAPS: True,
                        CONF_HISTORY_DAYS: DEFAULT_HISTORY_DAYS,
                    },
                )

        return self.async_show_form(
            step_id="authorize",
            description_placeholders={
                "authorization_url": self._auth_url,
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "authorization_code"
                    ): str
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get options flow."""
        return HuaweiHealthOptionsFlow(config_entry)


class HuaweiHealthOptionsFlow(
    config_entries.OptionsFlow
):
    """Huawei Health options flow."""

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input=None,
    ):
        """Manage options."""

        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        options = self._config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ENABLE_ACTIVITIES,
                        default=options.get(
                            CONF_ENABLE_ACTIVITIES,
                            True,
                        ),
                    ): bool,
                    vol.Required(
                        CONF_ENABLE_SLEEP,
                        default=options.get(
                            CONF_ENABLE_SLEEP,
                            True,
                        ),
                    ): bool,
                    vol.Required(
                        CONF_ENABLE_NAPS,
                        default=options.get(
                            CONF_ENABLE_NAPS,
                            True,
                        ),
                    ): bool,
                    vol.Required(
                        CONF_HISTORY_DAYS,
                        default=options.get(
                            CONF_HISTORY_DAYS,
                            DEFAULT_HISTORY_DAYS,
                        ),
                    ): vol.All(
                        int,
                        vol.Range(
                            min=1,
                            max=365,
                        ),
                    ),
                }
            ),
        )