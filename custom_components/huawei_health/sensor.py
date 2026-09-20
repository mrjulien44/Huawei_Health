from homeassistant.components.sensor import SensorEntity,SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
async def async_setup_entry(hass,entry,add_entities):add_entities([LastSync(hass.data[DOMAIN][entry.entry_id],entry)])
class LastSync(CoordinatorEntity,SensorEntity):
 _attr_has_entity_name=True;_attr_name='Dernière synchronisation';_attr_icon='mdi:cloud-sync';_attr_device_class=SensorDeviceClass.TIMESTAMP
 def __init__(self,c,e):super().__init__(c);self._attr_unique_id=f'{e.entry_id}_last_sync'
 @property
 def native_value(self):return self.coordinator.last_update_success_time
