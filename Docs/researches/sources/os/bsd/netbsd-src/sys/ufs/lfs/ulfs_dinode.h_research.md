# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dinode.h

## Scope

Small compatibility header for ULFS/LFS dinode-related mode bit definitions.

## APIs And Behavior

Defines traditional inode permission and special-mode constants: `IEXEC`, `IWRITE`, `IREAD`, `ISVTX`, `ISGID`, and `ISUID`.

## State And Dependencies

Includes `ufs/lfs/lfs.h` for surrounding LFS declarations. The constants are used by ULFS/LFS code that expects UFS-style inode mode names.

## Risks And Invariants

The numeric values must match standard Unix mode bits; changing them would break permission and special-mode interpretation across inode creation and attribute paths.
