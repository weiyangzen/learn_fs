# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fd_debug.h

## Role

`fd_debug.h` defines DEBUG-build error printing controls for floppy disk (`fd`) and controller/FC-style code paths.

## Debug Controls

- Defines severity levels `FDEP_L0` through `FDEP_L4` and `FDEP_LMAX`, where L0 is most verbose and L4 is catastrophic.
- In DEBUG builds, `FDERRPRINT()` and `FCERRPRINT()` call `cmn_err` only when the message level is at least the configured level and the function mask matches `fderrmask` or `fcerrmask`.
- In non-DEBUG builds, both macros compile to empty blocks.

## Function Masks

Defines `FDEM_*` mask bits for floppy driver functions and phases including identify/attach, size, open, label, close, strategy/start, read/write, command, execution, recovery, interrupt, watch, ioctls, raw ioctls, property operation, command-state block get/return, reset, recalibrate/seek, format, checkdisk, select, eject, change sense, packlabel, module init/info/fini, and `FDEM_ALL`.
