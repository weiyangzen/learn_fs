# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/env.h

## Purpose
Defines environmental-monitor sysevent payload attributes and state constants for temperature, power, fan, and LED events.

## Main Interfaces
- Common attributes:
  - `ENV_VERSION`
  - `ENV_FRU_ID`
  - `ENV_FRU_RESOURCE_ID`
  - `ENV_FRU_DEVICE`
  - `ENV_FRU_STATE`
  - `ENV_MSG`
  - `ENV_RESERVED_ATTR`
- FRU state constants:
  - `ENV_OK`
  - `ENV_WARNING`
  - `ENV_FAILED`
- LED state constants:
  - `ENV_LED_ON`
  - `ENV_LED_OFF`
  - `ENV_LED_BLINKING`
  - `ENV_LED_FLASHING`
  - `ENV_LED_INACCESSIBLE`
  - `ENV_LED_STANDBY`
  - `ENV_LED_NOT_PRESENT`

## Dependencies And Relationships
Schema comments target `EC_ENV` subclasses such as temp, power, fan, and LED. Producers are environmental monitor components.

## Research Notes
The file is schema-oriented. It standardizes attribute names and enumerated payload values but does not define the event class strings themselves.
