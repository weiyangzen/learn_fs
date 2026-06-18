# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/domain.h

## Purpose
Defines payload attribute names and values for domain state-change sysevents.

## Main Interfaces
- `DOMAIN_VERSION`
- `DOMAIN_WHAT_CHANGED`
- `DOMAIN_KEYSWITCH`
- `DOMAIN_FRU`
- `DOMAIN_RESERVED_ATTR`

## Dependencies And Relationships
Schema comments target `EC_DOMAIN` / `ESC_DOMAIN_STATE_CHANGE` events published by domain environment monitoring code.

## Research Notes
The header is a small event-schema vocabulary for consumers that interpret domain FRU or keyswitch state changes.
