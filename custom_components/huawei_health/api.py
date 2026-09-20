from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Iterable
from urllib.parse import urlencode
import aiohttp
from .const import ACTIVITY_PATH, HEALTH_RECORD_PATH, OAUTH_AUTHORIZE_URL, OAUTH_TOKEN_URL, SLEEP_DATA_TYPE
from .exceptions import HuaweiHealthApiError,HuaweiHealthAuthError,HuaweiHealthConnectionError
from .models import HuaweiCalendarItem
import logging
_LOGGER = logging.getLogger(__name__)

ACTIVITY_NAMES={1:"Marche",2:"Course",3:"Vélo",4:"Natation",5:"Randonnée",6:"Entraînement",7:"Escalade",8:"Ski",9:"Rameur",10:"Elliptique"}
SLEEP_NAMES={1:"Sommeil TruSleep",2:"Sommeil",3:"Sieste"}

class HuaweiHealthClient:
 def __init__(self,session:aiohttp.ClientSession,client_id:str,client_secret:str,redirect_uri:str,api_base:str,access_token:str|None=None):
  self.session=session; self.client_id=client_id; self.client_secret=client_secret; self.redirect_uri=redirect_uri; self.api_base=api_base.rstrip('/'); self.access_token=access_token
 def authorization_url(self,scopes:list[str],state:str)->str:
  return f"{OAUTH_AUTHORIZE_URL}?{urlencode({'response_type':'code','client_id':self.client_id,'redirect_uri':self.redirect_uri,'scope':' '.join(scopes),'access_type':'offline','state':state})}"
 async def exchange_code(self,code:str)->dict[str,Any]:
  token = await self._token_request({'grant_type':'authorization_code','code':code,'client_id':self.client_id,'client_secret':self.client_secret,'redirect_uri':self.redirect_uri})
  _LOGGER.warning("HUAWEI TOKEN=%s", token)
  return token
 async def refresh_token(self,token:str)->dict[str,Any]:
  return await self._token_request({'grant_type':'refresh_token','refresh_token':token,'client_id':self.client_id,'client_secret':self.client_secret})
 async def _token_request(self,data):
  try:
   async with self.session.post(OAUTH_TOKEN_URL,data=data,timeout=aiohttp.ClientTimeout(total=30)) as r:
    payload=await _json(r)
    if r.status>=400: raise HuaweiHealthAuthError(str(payload))
    return payload
  except aiohttp.ClientError as exc: raise HuaweiHealthConnectionError(str(exc)) from exc
 async def _get(self,path:str,params:dict[str,Any])->dict[str,Any]:
  if not self.access_token: raise HuaweiHealthAuthError('Missing access token')
  try:
   async with self.session.get(f"{self.api_base}/{path.lstrip('/')}",params=params,headers={'Authorization':f'Bearer {self.access_token}','x-client-id':self.client_id},timeout=aiohttp.ClientTimeout(total=45)) as r:
    payload=await _json(r)
    if r.status in (401,403): raise HuaweiHealthAuthError(str(payload))
    if r.status>=400: raise HuaweiHealthApiError(str(payload))
    return payload
  except aiohttp.ClientError as exc: raise HuaweiHealthConnectionError(str(exc)) from exc
 async def async_get_activities(self,start:datetime,end:datetime)->list[HuaweiCalendarItem]:
  payload=await self._get(ACTIVITY_PATH,_range_ns(start,end))
  records=_list(payload,'activityRecords','records','data')
  return sorted((x for x in (map_activity(r) for r in records) if x),key=lambda x:x.start)
 async def async_get_sleep(self,start:datetime,end:datetime,include_naps:bool)->list[HuaweiCalendarItem]:
  params={**_range_ns(start,end),'dataType':SLEEP_DATA_TYPE}
  payload=await self._get(HEALTH_RECORD_PATH,params)
  records=_list(payload,'healthRecords','records','data')
  values=[x for x in (map_sleep(r) for r in records) if x]
  if not include_naps: values=[x for x in values if x.category!='nap']
  return sorted(values,key=lambda x:x.start)

def map_activity(record:dict[str,Any])->HuaweiCalendarItem|None:
 start=_dt(_first(record,'startTime','start_time','start')); end=_dt(_first(record,'endTime','end_time','end'))
 if not start or not end or end<=start: return None
 typ=_first(record,'activityType','activity_type','type','sportType','sport_type')
 title=_first(record,'name','activityName','activity_name','title') or ACTIVITY_NAMES.get(_int(typ),f"Activité {typ}" if typ is not None else 'Activité sportive')
 summary=_dict(record.get('summary')); details=_dict(record.get('details')); stats={**details,**summary,**record}
 lines=[]
 _line(lines,'Durée',_duration(stats.get('duration') or (end-start).total_seconds()))
 _line(lines,'Distance',_distance(_first(stats,'distance','totalDistance','total_distance')))
 _line(lines,'Calories',_number(_first(stats,'calories','totalCalories','total_calories'),'kcal'))
 _line(lines,'Fréquence cardiaque moyenne',_number(_first(stats,'avgHeartRate','averageHeartRate','avg_heart_rate'),'bpm'))
 _line(lines,'Fréquence cardiaque maximale',_number(_first(stats,'maxHeartRate','max_heart_rate'),'bpm'))
 _line(lines,'Vitesse moyenne',_number(_first(stats,'avgSpeed','averageSpeed','avg_speed'),'m/s'))
 _line(lines,'Pas',_number(_first(stats,'steps','stepCount','step_count'),None,0))
 uid=str(_first(record,'id','activityRecordId','activity_record_id','recordId') or _uid('activity',start,end,title))
 location=_location(record)
 return HuaweiCalendarItem(f"activity:{uid}",'activity',start,end,str(title),'\n'.join(lines) or None,location)

def map_sleep(record:dict[str,Any])->HuaweiCalendarItem|None:
 data=_feature_data(record)
 start=_dt(_first(data,'fall_asleep_time','fallAsleepTime') or _first(record,'startTime','start_time'))
 end=_dt(_first(data,'wakeup_time','wakeupTime') or _first(record,'endTime','end_time'))
 if not start or not end or end<=start: return None
 sleep_type=_int(_first(data,'sleep_type','sleepType')) or 1
 title=SLEEP_NAMES.get(sleep_type,'Sommeil'); score=_first(data,'sleep_score','sleepScore')
 if score is not None: title+=f" - score {score}"
 lines=[]
 _line(lines,'Durée totale',_minutes(_first(data,'all_sleep_time','allSleepTime')))
 _line(lines,'Sommeil profond',_minutes(_first(data,'deep_sleep_time','deepSleepTime')))
 _line(lines,'Sommeil léger',_minutes(_first(data,'light_sleep_time','lightSleepTime')))
 _line(lines,'Sommeil paradoxal',_minutes(_first(data,'dream_time','dreamTime')))
 _line(lines,'Éveillé',_minutes(_first(data,'awake_time','awakeTime')))
 _line(lines,'Réveils',_number(_first(data,'wakeup_count','wakeupCount'),None,0))
 _line(lines,'Continuité du sommeil profond',_number(_first(data,'deep_sleep_part','deepSleepPart'),'points',0))
 uid=str(_first(record,'id','healthRecordId','health_record_id','recordId') or _uid('sleep',start,end,title))
 return HuaweiCalendarItem(f"sleep:{uid}",'nap' if sleep_type==3 else 'sleep',start,end,title,'\n'.join(lines) or None)

def _feature_data(r):
 for key in ('featureData','feature_data','data'):
  value=r.get(key)
  if isinstance(value,dict): return value
 points=r.get('samplePoints') or r.get('sample_points') or []
 if points and isinstance(points[0],dict): return _dict(points[0].get('fieldValue') or points[0].get('fieldValues') or points[0])
 return r
async def _json(r):
 try:return await r.json(content_type=None)
 except Exception:return {'message':await r.text()}
def _list(p,*keys):
 for k in keys:
  v=p.get(k)
  if isinstance(v,list): return v
  if isinstance(v,dict):
   for nested in ('items','records','data'):
    if isinstance(v.get(nested),list): return v[nested]
 return []
def _dict(v): return v if isinstance(v,dict) else {}
def _first(d,*keys):
 for k in keys:
  if d.get(k) is not None:return d[k]
 return None
def _int(v):
 try:return int(v)
 except (TypeError,ValueError):return None
def _dt(v):
 if isinstance(v,datetime):return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
 try:
  n=float(v); n=n/1_000_000_000 if n>1e17 else n/1000 if n>1e11 else n
  return datetime.fromtimestamp(n,tz=timezone.utc)
 except (TypeError,ValueError,OSError):return None
def _range_ns(s,e): return {'startTime':int(s.timestamp()*1_000_000_000),'endTime':int(e.timestamp()*1_000_000_000)}
def _uid(kind,s,e,title):return sha256(f'{kind}|{s.isoformat()}|{e.isoformat()}|{title}'.encode()).hexdigest()[:24]
def _line(lines,label,value):
 if value is not None:lines.append(f'{label} : {value}')
def _minutes(v):
 n=_int(v)
 return None if n is None else f'{n//60} h {n%60:02d}' if n>=60 else f'{n} min'
def _duration(v):
 try:
  n=int(float(v)); n=n//1000 if n>864000 else n
  return f'{n//3600} h {(n%3600)//60:02d}' if n>=3600 else f'{n//60} min'
 except (TypeError,ValueError):return None
def _distance(v):
 try:
  n=float(v); return f'{n/1000:.2f} km' if n>=1000 else f'{n:.0f} m'
 except (TypeError,ValueError):return None
def _number(v,unit=None,digits=1):
 try:
  n=float(v); text=f'{n:.{digits}f}'.rstrip('0').rstrip('.'); return f'{text} {unit}' if unit else text
 except (TypeError,ValueError):return None
def _location(r):
 loc=r.get('location')
 if isinstance(loc,str):return loc
 if isinstance(loc,dict):return loc.get('name') or loc.get('address')
 return None
