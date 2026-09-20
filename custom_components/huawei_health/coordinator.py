# from datetime import timedelta
# import logging
# from homeassistant.helpers.update_coordinator import DataUpdateCoordinator,UpdateFailed
# from homeassistant.util import dt as dt_util
# from .const import DEFAULT_SCAN_INTERVAL
# from .exceptions import HuaweiHealthError
# from .models import HuaweiHealthData
# _LOGGER=logging.getLogger(__name__)
# class HuaweiHealthCoordinator(DataUpdateCoordinator[HuaweiHealthData]):
#  def __init__(self,hass,entry,client):super().__init__(hass,_LOGGER,name='Huawei Health',update_interval=DEFAULT_SCAN_INTERVAL);self.entry=entry;self.client=client
#  async def _async_update_data(self):
#   now=dt_util.now(); start=now-timedelta(days=int(self.entry.options.get('history_days',30)));end=now+timedelta(days=1)
#   try:
#    a=await self.client.async_get_activities(start,end) if self.entry.options.get('enable_activities',True) else []
#    s=await self.client.async_get_sleep(start,end,self.entry.options.get('enable_naps',True)) if self.entry.options.get('enable_sleep',True) else []
# #    s=await self.client.async_get_sleep(start,end,self.entry.options.get('enable_naps',True)) if self.entry.options.get('enable_sleep',True) else []
#    return HuaweiHealthData(a,s)
#   except HuaweiHealthError as exc:raise UpdateFailed(str(exc)) from exc

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
            # Sommeil désactivé
            #
            sleep = []

            return HuaweiHealthData(
                activities=activities,
                sleep=sleep,
            )

        except HuaweiHealthError as exc:
            raise UpdateFailed(str(exc)) from exc