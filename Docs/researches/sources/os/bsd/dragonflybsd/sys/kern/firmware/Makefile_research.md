# File Research: sources/os/bsd/dragonflybsd/sys/kern/firmware/Makefile

## Summary
Kernel module makefile for the firmware subsystem.

## Main Contents
- Sets `.PATH` to the parent kernel directory.
- Builds `KMOD=firmware`.
- Uses `subr_firmware.c` as the only source.
- Includes `bsd.kmod.mk`.

## Risks
The module source is outside the `firmware` directory via `.PATH`, so build and source ownership are split between this subdirectory and `sys/kern/subr_firmware.c`.
