# File Research: sources/local-fs/btrfs-progs/kernel-lib/sizes.h

## Purpose
Linux-style size constants for powers of two from bytes through GiB.

## Contents
Defines `SZ_1` through `SZ_512`, `SZ_1K` through `SZ_512K`, `SZ_1M` through `SZ_512M`, and `SZ_1G`/`SZ_2G`.

## Integration
Used by mkfs sizing code, especially `mkfs/common.h` and `mkfs/common.c`.

## Risks
Constants are untyped integer macros. Large values such as `SZ_2G` may need explicit casting in signed 32-bit contexts.
