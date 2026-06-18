# File Research: sources/local-fs/e2fsprogs/e2fsck/flushb.c

## Purpose
Standalone benchmarking helper to flush a block device’s buffer cache.

## Main Behavior
- CLI: `flushb disk`.
- Opens the device read-only.
- On Linux or systems defining `BLKFLSBUF`, invokes `ioctl(fd, BLKFLSBUF, 0)`.
- Reports unsupported ioctl otherwise.

## Integration
Built as optional helper target `flushb` in `Makefile.in`. The file comment warns it is not generally useful outside benchmarking scripts.

## Risks / Notes
The file explicitly warns older Linux 2.2 kernels could corrupt filesystems under heavy load when using this operation.
