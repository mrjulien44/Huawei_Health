from homeassistant.components.diagnostics import async_redact_data
from .const import CONF_ACCESS_TOKEN,CONF_REFRESH_TOKEN
async def async_get_config_entry_diagnostics(hass,entry):return {'entry':async_redact_data(dict(entry.data),{CONF_ACCESS_TOKEN,CONF_REFRESH_TOKEN,'client_secret'}),'options':dict(entry.options)}
