# sources/user-network-fs/mergerfs/src/fuse_init.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_init.cpp` negotiates FUSE connection capabilities and logs runtime configuration. The source was read as a complete 244-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::init`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::init` initializes procfs/readdir config, requests supported capabilities, adjusts max-pages/sysfs limits, spawns detached readahead setup, validates passthrough/cache combinations, and logs config.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_init.hpp", "config.hpp", "fs_readahead.hpp", "procfs.hpp", "state.hpp", "syslog.hpp", "fs_path.hpp", "fs_exists.hpp". Startup-critical; risks include sysfs permissions, detached readahead timing, and kernel capability mismatches.

## Risks and Edge Cases

Startup-critical; risks include sysfs permissions, detached readahead timing, and kernel capability mismatches.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
