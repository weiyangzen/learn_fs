# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/cityhash.h

Read status: complete, 41 lines.

Purpose: declaration for a small CityHash-derived hash helper.

Key API:
- `uint64_t cityhash4(uint64_t, uint64_t, uint64_t, uint64_t);`

Dependencies: `zfs_context.h`.

Research notes:
- The header includes the upstream Google permissive license notice and a Delphix copyright.
- It exposes only a four-word 64-bit hash function, not the full CityHash API.
