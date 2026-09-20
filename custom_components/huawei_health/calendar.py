from datetime import datetime
from homeassistant.components.calendar import CalendarEntity,CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
async def async_setup_entry(hass,entry,add_entities):
 c=hass.data[DOMAIN][entry.entry_id];add_entities([HuaweiCalendar(c,entry,'activities','Activités','mdi:run'),HuaweiCalendar(c,entry,'sleep','Sommeil','mdi:sleep')])
class HuaweiCalendar(CoordinatorEntity,CalendarEntity):
 _attr_has_entity_name=True
 def __init__(self,c,e,key,name,icon):super().__init__(c);self._key=key;self._attr_name=name;self._attr_icon=icon;self._attr_unique_id=f'{e.entry_id}_{key}'
 @property
 def _items(self):return getattr(self.coordinator.data,self._key,[]) if self.coordinator.data else []
 @staticmethod
 def _event(x):return CalendarEvent(summary=x.summary,start=x.start,end=x.end,description=x.description,location=x.location,uid=x.uid)
 @property
 def event(self):
  from homeassistant.util import dt as dt_util
  c=[x for x in self._items if x.end>=dt_util.now()];return self._event(min(c,key=lambda x:x.start)) if c else None
 async def async_get_events(self,hass,start_date:datetime,end_date:datetime):return [self._event(x) for x in sorted(self._items,key=lambda y:y.start) if x.end>start_date and x.start<end_date]
