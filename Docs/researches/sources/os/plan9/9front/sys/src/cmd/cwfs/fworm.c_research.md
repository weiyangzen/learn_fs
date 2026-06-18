# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/fworm.c

Fake-WORM device adapter. It reserves a bitmap at the end of an underlying device to record which logical blocks have been written, enforcing write-once semantics over a regular block device.

Important behavior:
- `fwormsize()` subtracts bitmap storage from the underlying device size.
- `fwormream()` zeroes and tags bitmap blocks as `Tvirgo`.
- `fwormread()` checks the bitmap before reading; unwritten blocks return an error.
- `fwormwrite()` fails if the block was already marked written, otherwise marks it and writes data.
- Bounds and tag failures panic because they indicate structural corruption or misuse.
