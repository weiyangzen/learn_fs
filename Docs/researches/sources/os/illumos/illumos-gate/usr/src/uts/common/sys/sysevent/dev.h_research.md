# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/dev.h

## Purpose
Defines public device sysevent payload schemas and attribute names for device add/remove and device-branch events.

## Main Interfaces
- Attribute names:
  - `EV_VERSION`
  - `DEV_PHYS_PATH`
  - `DEV_NAME`
  - `DEV_DRIVER_NAME`
  - `DEV_INSTANCE`
  - `DEV_PROP_PREFIX`
- Version constant `EV_V1`.
- Property limits:
  - `MAX_PROP_COUNT`
  - `PROP_LEN_LIMIT`

## Dependencies And Relationships
Includes `sys/sysevent/eventdefs.h` for device class/subclass names such as device add/remove and branch add/remove. Used by device tree and devfs event producers.

## Research Notes
The schema comments cover disk, network, printer, and device-branch events. Add events may include selected devinfo node properties via the `prop-` prefix; remove events use the core identifying fields.
