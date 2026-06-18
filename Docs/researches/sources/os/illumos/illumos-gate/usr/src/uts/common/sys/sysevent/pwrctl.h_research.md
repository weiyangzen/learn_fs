# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/pwrctl.h

## Purpose
Defines power-control sysevent schema details for ACPI/power-related add, remove, warning, low, state-change, button, and brightness events.

## Main Interfaces
- The file documents common attributes for `EC_PWRCTL` events, including version, ACPI hardware ID, UID, device index, and event-specific fields.
- `PWRCTL_BRIGHTNESS_LEVEL`: brightness-level payload attribute for brightness events.

## Dependencies And Relationships
Pairs with `EC_PWRCTL` and `ESC_PWRCTL_*` constants in `eventdefs.h`. Producers are power-control and ACPI/environmental monitor paths.

## Research Notes
Most of the contract is carried in comments describing the schema. The only macro in the file is the brightness-level attribute name.
