# sources/user-network-fs/mergerfs/src/fs_inode.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_inode.cpp` implements mergerfs virtual inode-number calculation algorithms. The source was read as a complete 404-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `set_algo`, `get_algo`, `calc`, `ReaddirCalc::calc`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`set_algo`, `get_algo`, `calc`, and `ReaddirCalc::calc` select and apply passthrough, path hash, dev+ino hash, and hybrid variants using rapidhash.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_inode.hpp", "rapidhash/rapidhash.h", <atomic>, <sys/stat.h>. Integrated by getattr/readdir/fgetattr so FUSE sees stable inode numbers. Hash32 modes can collide; passthrough can collide across branches.

## Risks and Edge Cases

Integrated by getattr/readdir/fgetattr so FUSE sees stable inode numbers. Hash32 modes can collide; passthrough can collide across branches.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
