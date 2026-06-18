# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/statfs.h

## Role

Legacy `statfs(2)`/`fstatfs(2)` ABI header, superseded by `statvfs`.

## Key Contents

Defines `struct statfs` with filesystem type, block size, fragment size, block counts, inode counts, volume name, and pack name. Defines `struct statfs32` for 32-bit syscall compatibility.

## Interfaces

For non-kernel code, declares `statfs` and `fstatfs`.

## Design Notes

The header states this interface has been replaced by `statvfs`/`fstatvfs` and may be removed in a future release.
