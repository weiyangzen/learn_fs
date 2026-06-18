# File Research: sources/local-fs/mtd-utils/mtd_debug.c

## Purpose
Debug utility for inspecting, reading, writing, and erasing raw MTD devices.

## Key Elements
Supports `info`, `read`, `write`, and `erase` subcommands. Wraps `MEMGETINFO`, `MEMERASE`, `MEMGETREGIONCOUNT`, and `MEMGETREGIONINFO`; prints device type/capability/geometry; copies flash ranges to files; copies files to flash; and erases requested ranges.

## Dependencies
Uses Linux MTD ioctls from `mtd/mtd-user.h`, POSIX file APIs, and `common.h`.

## Behavior/Risks
Raw write and erase operations are destructive and do not perform bad-block, erase-before-write, or alignment policy beyond the caller’s arguments. `file_to_flash()` does not verify short `write()` results, so partial writes can be missed.
