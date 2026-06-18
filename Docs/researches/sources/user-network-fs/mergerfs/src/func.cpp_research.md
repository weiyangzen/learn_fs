# sources/user-network-fs/mergerfs/src/func.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/func.cpp` parses configured policy names for FUSE operation policy slots. The source was read as a complete 77-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `Func::Base::{Action,Create,Search}::from_string`, `to_string`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`Func::Base::{Action,Create,Search}::from_string` looks up a policy implementation and `to_string` returns the selected policy name.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "func.hpp". Integrated by config parsing. Unknown policy names return `-EINVAL`.

## Risks and Edge Cases

Integrated by config parsing. Unknown policy names return `-EINVAL`.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
