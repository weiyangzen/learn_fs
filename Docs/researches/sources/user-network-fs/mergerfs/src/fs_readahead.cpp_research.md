# sources/user-network-fs/mergerfs/src/fs_readahead.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_readahead.cpp` sets block-device readahead for a device or path. The source was read as a complete 87-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `readahead`, `/sys/class/bdi/<major>:<minor>/read_ahead_kb`, `st_dev`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`readahead` derives `/sys/class/bdi/<major>:<minor>/read_ahead_kb`, writes the requested size, or stats a path to derive `st_dev`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_readahead.hpp", "fmt/core.h", "fs_lstat.hpp", <fstream>, <string>. Called during FUSE init for mountpoint and branches. It returns success even when sysfs open/write does not happen.

## Risks and Edge Cases

Called during FUSE init for mountpoint and branches. It returns success even when sysfs open/write does not happen.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
