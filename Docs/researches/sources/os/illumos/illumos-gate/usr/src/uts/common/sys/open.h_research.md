# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/open.h

## Purpose

`open.h` defines illumos device-driver open/close type constants. These constants let drivers distinguish why a device is being opened or closed and maintain correct per-minor usage state.

## Open Types

The file defines `OTYPCNT` as 5 and the five open types:

- `OTYP_BLK`: block special file open/close.
- `OTYP_MNT`: filesystem mount/unmount open/close.
- `OTYP_CHR`: character special file open/close.
- `OTYP_SWP`: swapping device open/close.
- `OTYP_LYR`: layered-driver open/close without a file directly open on the lower device.

The comments document protocol differences. The first four types may have many opens but only one close on last close for that minor/type, so a boolean state flag can work. `OTYP_LYR` opens and closes are always paired, so drivers should use counters.

## Research Notes

This is a stable kernel ABI header. Misinterpreting the close protocol is the main bug risk: using a boolean for layered opens or a counter-only model for last-close types can cause premature detach, leaked holds, or incorrect busy checks.
