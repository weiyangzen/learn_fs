# File Research: sources/os/linux/linux/fs/jfs/jfs_extent.h

## Role

Declares the JFS extent allocation interface and the inode-location allocation hint macro.

## Key Responsibilities

- Defines `INOHINT(ip)` as the last block of the disk inode extent, used as a placement hint for file data allocation.
- Declares `extAlloc()` for allocating and recording file extents.
- Declares `extHint()` for deriving a previous-page extent hint.
- Declares `extRecord()` for converting not-recorded extent metadata to recorded.

## Important Interactions

- Depends on `JFS_IP(ip)->ixpxd`, the disk inode extent descriptor maintained by inode-map code.
- Public functions are implemented in `jfs_extent.c` and used by file/block mapping code elsewhere in JFS.

## Invariants and Risks

- `INOHINT()` assumes `ixpxd` is valid and non-empty.
- Callers must pass an `xad_t` whose address field may contain an allocation hint on entry and receives the allocated extent on success.
