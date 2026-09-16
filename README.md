# Utility Cost v1.1.0

A HACS **custom integration** for Home Assistant with an included Lovelace card. It estimates electricity costs from live power sensors, preserves accumulated historical cost when rates change, handles TOU import pricing, daily supply charges and two-tier solar FIT, and tracks selected devices.

## Install with HACS

1. Put this repository on GitHub with `custom_components/utility_cost` at the repository root.
2. HACS → Integrations → ⋮ → Custom repositories.
3. Add the repository URL with category **Integration**.
4. Download **Utility Cost**, then restart Home Assistant.
5. Settings → Devices & services → Add Integration → **Utility Cost**.
6. Confirm the suggested grid/house/solar entities and select the device power entities to track.
7. Confirm the tariff settings.

The included card is served by the integration. If Home Assistant cannot auto-register the resource, add `/utility_cost/utility-cost-card.js` as a JavaScript module in Dashboard Resources.

Add a manual card:
```yaml
type: custom:utility-cost-card
```

## Current tariff defaults
- Peak: AUD 0.581713/kWh — 06:00–10:00 and 16:00–00:00
- Shoulder: AUD 0.210584/kWh — 10:00–16:00
- Off-peak: AUD 0.348018/kWh — 00:00–06:00
- Supply: AUD 1.260600/day
- FIT: AUD 0.08/kWh for first 10 kWh exported/day, then AUD 0.03/kWh

## Important
This is a bill **estimate** based on Home Assistant sensor data. Device figures are tariff-equivalent consumption costs; self-consumed solar cannot be assigned to individual appliances without circuit/source-level metering.

### Changing plan later
Settings → Devices & services → Utility Cost → Configure. Existing accumulated dollar totals remain; new consumption uses the newly saved rates.


## v1.1.0 frontend fix
The bundled Lovelace card is now served at `/utility_cost_static/utility-cost-card.js` and injected into the Home Assistant frontend automatically when the integration loads. No separate Dashboard HACS repository or manual Lovelace resource entry is required. After updating, restart Home Assistant and use `type: custom:utility-cost-card`.


## Utility Bill card

Version 1.1.0 adds a second bundled Lovelace card designed like an electricity bill. It supports Today, This week, This month and Bill period views, with tariff breakdown, supply charge, solar credit, usage summaries and tracked-device costs.

```yaml
type: custom:utility-bill-card
default_period: bill
```

If you register resources manually, add both as JavaScript modules:

- `/utility_cost_static/utility-cost-card.js?v=110`
- `/utility_cost_static/utility-bill-card.js?v=110`
