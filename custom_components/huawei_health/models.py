from dataclasses import dataclass
from datetime import datetime
@dataclass(frozen=True,slots=True)
class HuaweiCalendarItem:
    uid:str; category:str; start:datetime; end:datetime; summary:str; description:str|None=None; location:str|None=None
@dataclass(slots=True)
class HuaweiHealthData:
    activities:list[HuaweiCalendarItem]; sleep:list[HuaweiCalendarItem]
