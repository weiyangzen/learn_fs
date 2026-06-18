# File Research: sources/os/bsd/dragonflybsd/sys/sys/wdog.h

## Summary
Watchdog kernel registration structure and user ioctl constant.

## Main Responsibilities
- Defines watchdog callback type.
- Defines `struct watchdog` with public driver fields and internal period/list fields.
- Declares kernel register/unregister/disable helpers.
- Defines `WDIOCRESET` ioctl and default period.

## Important Behavior
Drivers provide a max period and callback argument, while the framework manages current period and list linkage internally.

## Risks
The structure warns internal fields should not be touched. Incorrect period handling can disable or misprogram watchdog hardware.
