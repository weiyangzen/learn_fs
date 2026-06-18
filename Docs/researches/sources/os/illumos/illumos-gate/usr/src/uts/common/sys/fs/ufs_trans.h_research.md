# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_trans.h

## Role

Defines UFS transaction/logging operation types, delta types, transaction wrapper macros, reservation-size calculations, debug matamap hooks, and transaction-layer prototypes.

## Key Enums

- `delta_t` classifies logged metadata/userdata deltas: superblock, cylinder group, summary info, allocation block, directory, inode, quota record, commit/cancel/BOT/EOT, userdata, scan userdata, shadow inode, and max.
- `top_t` classifies transaction operations: read/write, setattr/create/remove/link/rename/mkdir/rmdir/symlink/fsync, getpage/putpage, superblock updates, syncip variants, mount/commit/quota/itrunc/allocsp, and max.

## Transaction Macros

- `TRANS_ISTRANS()` tests whether logging is active via `ufsvfsp->vfs_log`.
- Begin/end wrappers handle sync, async, conditional sync, and try-begin variants.
- Delta wrappers log/cancel/check ranges and set/check log error state.
- Metadata helpers log buffers, 128-byte buffer items, full inode, inode timestamp ranges, summary info, directory blocks, quotas, dq releases, truncation, and write reservation/write execution.
- Wrapper macros route superblock update/write, syncip, and inode update through transaction-aware paths.
- DEBUG-only matamap macros maintain metadata checking state.

## Reservation Sizes

Defines estimated and calculated log reservation sizes for inode, superblock, directory, cylinder group, fragment, ACL, quota, create/remove/link/rename/mkdir/symlink/getpage/rmdir/setattr/ifree/mount/commit, and maximum per-operation reservation `TOP_MAX_RESV`.

## Interfaces

Kernel prototypes cover transaction hlock/onerror, metadata push callbacks, transaction-aware UFS operations, matamap debug operations, write/trunc reservation, LUFS snarf/unsnarf, top-layer delta/cancel/log/begin/end/error functions, and matamap mutation.

## Risk Notes

This header controls when UFS operations are journaled and how much log space they reserve. Incorrect transaction size estimates can deadlock or fail operations under log pressure; missing deltas can corrupt logged recovery.
