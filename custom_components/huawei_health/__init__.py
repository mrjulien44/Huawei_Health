from homeassistant.const import CONF_CLIENT_ID,CONF_CLIENT_SECRET
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import HuaweiHealthClient
from .const import *
from .coordinator import HuaweiHealthCoordinator
async def async_setup_entry(hass,entry):
 client=HuaweiHealthClient(async_get_clientsession(hass),entry.data[CONF_CLIENT_ID],entry.data[CONF_CLIENT_SECRET],entry.data[CONF_REDIRECT_URI],REGION_API_BASE[entry.data[CONF_REGION]],entry.data.get(CONF_ACCESS_TOKEN))
 c=HuaweiHealthCoordinator(hass,entry,client);await c.async_config_entry_first_refresh();hass.data.setdefault(DOMAIN,{})[entry.entry_id]=c
 await hass.config_entries.async_forward_entry_setups(entry,PLATFORMS);entry.async_on_unload(entry.add_update_listener(_reload));return True
async def async_unload_entry(hass,entry):
 ok=await hass.config_entries.async_unload_platforms(entry,PLATFORMS)
 if ok:hass.data[DOMAIN].pop(entry.entry_id)
 return ok
async def _reload(hass,entry):await hass.config_entries.async_reload(entry.entry_id)
