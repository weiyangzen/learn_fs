# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_version.h

## Role

Defines USB driver interface version constants for client drivers.

## Key Interfaces

- Defines `USBDRV_MAJOR_VER` as `2`.
- Defines `USBDRV_MINOR_VER` as `0`.

## Risk Notes

These constants participate in USBA driver/header version checks. Changing them affects source compatibility for USB client drivers.
