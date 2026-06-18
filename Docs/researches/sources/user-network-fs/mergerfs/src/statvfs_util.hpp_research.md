# sources/user-network-fs/mergerfs/src/statvfs_util.hpp

## Purpose
Provides inline calculations for `struct statvfs` fields.

## Important APIs, Types, and Functions
`StatVFS::readonly()` checks `ST_RDONLY`; `spaceavail()` returns `f_frsize * f_bavail`; `spaceused()` returns `f_frsize * (f_blocks - f_bavail)`.

## Control Flow
All helpers are single-expression calculations.

## State and Persistence Behavior
No state is retained. They summarize caller-provided statvfs snapshots.

## Dependencies and Integration Points
Used by filesystem info and policy code to normalize free/used/readonly values.

## Risks and Edge Cases
Multiplication can overflow signed `s64` on very large filesystems. `f_bavail` reflects unprivileged availability, not necessarily root-reserved capacity.

## Test Signals
Test readonly flags, expected byte calculations, large values, and consistency with `fs::info()` consumers.
