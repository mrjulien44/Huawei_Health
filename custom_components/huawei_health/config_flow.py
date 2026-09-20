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

from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import DEFAULT_SCAN_INTERVAL
from .exceptions import HuaweiHealthError
from .models import HuaweiHealthData

_LOGGER = logging.getLogger(__name__)


class HuaweiHealthCoordinator(
    DataUpdateCoordinator[HuaweiHealthData]
):
    def __init__(self, hass, entry, client):
        super().__init__(
            hass,
            _LOGGER,
            name="Huawei Health",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

        self.entry = entry
        self.client = client

    async def _async_update_data(self):
        now = dt_util.now()

        start = now - timedelta(
            days=int(
                self.entry.options.get(
                    "history_days",
                    30,
                )
            )
        )

        end = now + timedelta(days=1)

        try:
            #
            # ACTIVITÉS UNIQUEMENT
            #
            activities = (
                await self.client.async_get_activities(
                    start,
                    end,
                )
                if self.entry.options.get(
                    "enable_activities",
                    True,
                )
                else []
            )

            #
            # DÉSACTIVÉ TEMPORAIREMENT
            # Les comptes Huawei individuels
            # semblent être bloqués sur les
            # données sommeil (403 scopes).
            #
            sleep = []

            return HuaweiHealthData(
                activities=activities,
                sleep=sleep,
            )

        except HuaweiHealthError as exc:
            raise UpdateFailed(str(exc)) from exc