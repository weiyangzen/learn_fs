# File Research: sources/os/linux/linux/fs/befs/Kconfig

## Summary
Defines configuration options for the Linux BeFS filesystem driver.

## Main Contents
- `BEFS_FS`: tristate read-only BeOS filesystem support.
- `BEFS_DEBUG`: optional debug support depending on `BEFS_FS`.

## Important Behavior
`BEFS_FS` depends on block-device support and selects `BUFFER_HEAD` and `NLS`. The help text notes the driver is read-only and does not expose BeFS attributes or database-like indices.

`BEFS_DEBUG` enables driver debugging output usable with the `debug` mount option.

## Risks
No runtime logic. Enabling debug changes compilation through the Makefile’s `-DDEBUG`.
