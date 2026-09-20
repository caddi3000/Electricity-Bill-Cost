# Electricity Bill Cost v1.2.1

Lovelace bill-style frontend card for the **Utility Cost** Home Assistant integration.

This repository is a **HACS Dashboard/Plugin** repository. It does not provide the accounting backend. Install/update `caddi3000/Utility-Costings` as a HACS **Integration** first.

## Card

```yaml
type: custom:utility-bill-card
default_period: bill
```

The card reads the sensors produced by the Utility Cost integration and shows:

- Today, week, month and bill-period views
- Estimated retailer bill
- Peak / Shoulder / Off-peak grid-import kWh and cost
- Daily supply charge
- Solar FIT credit
- Grid import, solar export, house consumption and solar generation
- Per-device Peak / Shoulder / Off-peak energy and tariff-cost breakdowns

## HACS

Add this repository as a **Dashboard/Plugin** repository. HACS should serve the card from its normal `/hacsfiles/` resource path and normally registers the resource automatically.

## Required backend

Requires Utility Cost v1.2.1 or later from `caddi3000/Utility-Costings`.

Tariffs and monitored entities are configured in Home Assistant at **Settings → Devices & services → Integrations → Utility Cost → Configure**.

## Cost meaning

The main bill estimate is grid import charges + supply charge − solar FIT credit. Device values are tariff costs based on when each tracked device consumed energy. They are intentionally separate from the retailer bill estimate because whole-home solar monitoring cannot identify exactly which appliance consumed each unit of self-generated solar.
