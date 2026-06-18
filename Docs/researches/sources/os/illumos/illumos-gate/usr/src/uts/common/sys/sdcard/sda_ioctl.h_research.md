# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda_ioctl.h

## Role

Defines private ioctl data shared between the SD card `cfgadm` plugin and the illumos SDA framework.

## Key Interfaces

- `sda_card_type_t` enumerates unknown, MMC, SD memory, SDHC, SD combo, and SDIO card classes.
- `sda_card_info_t` reports card type plus memory-card identity fields: manufacturer, OEM ID, product ID, serial, date, and revision.
- `struct sda_ap_control` carries AP-control command, payload size, and payload pointer.
- Kernel-only `struct sda_ap_control32` provides ILP32-compatible fields.

## Commands

Defines AP-control commands for card-info lookup, device-path lookup, and slot reset:
`SDA_CFGA_GET_CARD_INFO`, `SDA_CFGA_GET_DEVICE_PATH`, `SDA_CFGA_RESET_SLOT`.

## Risk Notes

This is a private plugin/kernel control ABI. Structure layout, command numbering, and 32-bit compatibility fields must stay synchronized with both cfgadm-side and framework-side consumers.
