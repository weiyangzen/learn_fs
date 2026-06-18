# File Research: sources/teaching/minix/minix/drivers/storage/mmc/Makefile

## Purpose

Builds the MINIX MMC/SD block driver variants.

## Build Role

Defines two programs: `mmc` and `emmc`. `mmc` builds from `mmcblk.c`, `mmchost_dummy.c`, `mmchost_mmchs.c`, and register headers. `emmc` builds from `emmc.c` and `mmcblk.c`. Both link against `libblockdriver` and `libsys`, set `_SYSTEM=1`, and include `minix.service.mk`.

## Dependencies

Depends on MINIX system-driver privileges, the generic MMC block layer, host-controller implementations, and SD/MMC register headers.

## Risks

The `emmc` target reuses `mmcblk.c` while providing host initialization from `emmc.c`; duplicate host initializer stubs in `emmc.c` are intentional but easy to confuse with the regular `mmc` host selection path.
