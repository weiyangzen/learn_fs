# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/devio.c

## Purpose
Implements raw sector read/write helpers for a mounted FAT filesystem device.

## Key Behavior
- `devread()` performs `pread()` at `xf->offset + addr * xf->sectsize` and returns zero only on full read.
- `devwrite()` refuses writes when the underlying device was opened read-only, then performs `pwrite()` at the same translated offset.
- `deverror()` records `Eio`, closes the device on system-call errors, logs short transfers, and returns failure.

## Interfaces And Dependencies
- Uses `Xfs` from `dat.h` and `chat()` diagnostics.
- Called by the `iotrack` sector cache for actual media I/O.

## Notes
The `xf->offset` field lets `dossrv` mount a FAT filesystem embedded at a byte offset inside another file/device.
