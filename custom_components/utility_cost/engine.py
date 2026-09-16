from __future__ import annotations
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util
from .const import *

PERIODS=("today","week","month","bill","year")
class CostEngine:
    def __init__(self,hass:HomeAssistant,entry):
        self.hass=hass; self.entry=entry; self.store=Store(hass,2,"utility_cost_state")
        self.data={}; self.last=None; self.listeners=[]
    @property
    def cfg(self): return {**DEFAULTS, **self.entry.data, **self.entry.options}
    async def load(self):
        self.data=await self.store.async_load() or {"periods":{},"fit_day_kwh":0.0,"fit_day":None,"tariff_history":[]}
        self.data.setdefault("periods",{}); self.data.setdefault("tariff_history",[]); self.data.setdefault("started_at", dt_util.now().isoformat())
        self._ensure_periods(dt_util.now())
    def _bill_bounds(self,now):
        start=dt_util.parse_date(str(self.cfg[CONF_BILL_START])) or now.date()
        if now.date()<start: return start,start
        delta=(now.date()-start).days
        # Bill cycles repeat on the cadence implied by the configured start; default is quarterly.
        cycle_days=91
        cycle_start=start+timedelta(days=(delta//cycle_days)*cycle_days)
        return cycle_start,cycle_start+timedelta(days=cycle_days-1)
    def _keys(self,now):
        week_start=now.date()-timedelta(days=now.weekday())
        bill_start,_=self._bill_bounds(now)
        return {"today":now.date().isoformat(),"week":week_start.isoformat(),"month":now.strftime("%Y-%m"),"year":str(now.year),"bill":bill_start.isoformat()}
    def _blank(self): return {"grid":0.0,"grid_kwh":0.0,"supply":0.0,"fit":0.0,"export_kwh":0.0,"solar_kwh":0.0,"devices":{},"device_kwh":{},"tracked_kwh":0.0,"house_kwh":0.0,"tariff_kwh":{"peak":0.0,"shoulder":0.0,"offpeak":0.0},"tariff_cost":{"peak":0.0,"shoulder":0.0,"offpeak":0.0}}
    def _ensure_periods(self,now):
        keys=self._keys(now)
        for p,k in keys.items():
            item=self.data["periods"].get(p)
            if not item or item.get("key")!=k:self.data["periods"][p]={"key":k,**self._blank()}
            else:
                for key,val in self._blank().items(): item.setdefault(key,val.copy() if isinstance(val,dict) else val)
        day=now.date().isoformat()
        if self.data.get("fit_day")!=day:self.data["fit_day"]=day;self.data["fit_day_kwh"]=0.0
    def tariff(self,now):
        m=now.hour*60+now.minute
        if 360<=m<600 or 960<=m<1440:return "peak",float(self.cfg[CONF_PEAK])
        if 600<=m<960:return "shoulder",float(self.cfg[CONF_SHOULDER])
        return "offpeak",float(self.cfg[CONF_OFFPEAK])
    def _power_kw(self,eid):
        st=self.hass.states.get(eid)
        if not st:return 0.0
        try:v=float(st.state)
        except (ValueError,TypeError):return 0.0
        unit=st.attributes.get("unit_of_measurement","")
        return v if unit=="kW" else v/1000.0
    async def tick(self,now=None):
        now=now or dt_util.now();self._ensure_periods(now)
        if self.last is None:self.last=now;return
        hours=max(0,min((now-self.last).total_seconds()/3600,0.1));self.last=now
        if not hours:return
        tariff,rate=self.tariff(now);c=self.cfg
        imp=max(0,self._power_kw(c[CONF_GRID_IMPORT]));exp=max(0,self._power_kw(c[CONF_GRID_EXPORT]));house=max(0,self._power_kw(c[CONF_HOUSE_POWER]));solar=max(0,self._power_kw(c.get(CONF_SOLAR_POWER,"")))
        tracked=list(c.get(CONF_TRACKED) or []);dev={e:max(0,self._power_kw(e)) for e in tracked}
        import_kwh=imp*hours;export_kwh=exp*hours;used=float(self.data.get("fit_day_kwh",0));lim=float(c[CONF_FIT_LIMIT]);tier1=max(0,min(export_kwh,lim-used));tier2=max(0,export_kwh-tier1);fit=tier1*float(c[CONF_FIT1])+tier2*float(c[CONF_FIT2]);self.data["fit_day_kwh"]=used+export_kwh
        for p in PERIODS:
            x=self.data["periods"][p];x["grid"]+=import_kwh*rate;x["grid_kwh"]+=import_kwh;x["supply"]+=float(c[CONF_SUPPLY])*hours/24;x["fit"]+=fit;x["export_kwh"]+=export_kwh;x["house_kwh"]+=house*hours;x["solar_kwh"]+=solar*hours;x["tariff_kwh"][tariff]+=import_kwh;x["tariff_cost"][tariff]+=import_kwh*rate
            for e,kw in dev.items():x["devices"][e]=x["devices"].get(e,0)+kw*hours*rate;x["device_kwh"][e]=x["device_kwh"].get(e,0)+kw*hours;x["tracked_kwh"]+=kw*hours
        await self.store.async_save(self.data)
        for cb in list(self.listeners):cb()
    def period(self,p):return self.data["periods"].get(p,self._blank())
