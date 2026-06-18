# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/datalink.h

## Purpose
Defines payload attribute names for datalink sysevents, specifically link-state events.

## Main Interfaces
- `DATALINK_EV_LINK_NAME`: datalink name attribute.
- `DATALINK_EV_LINK_ID`: `datalink_id_t` attribute.
- `DATALINK_EV_ZONE_ID`: zone ID attribute.

## Dependencies And Relationships
The comments define the schema for `EC_DATALINK` / `EC_DATALINK_LINK_STATE` events. Actual class/subclass strings are supplied by sysevent event definition headers.

## Research Notes
This is a schema-name header only; it deliberately contains no functions or structures.
