# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_rlock.h

Defines ZFS range-lock structures for coordinating byte-range reads, writes, appends, truncates, and hole punching.

Key elements:
- `rangelock_type_t` has `RL_READER`, `RL_WRITER`, and `RL_APPEND`.
- `rangelock_t` contains an AVL tree, mutex, callback, and callback argument.
- `locked_range_t` records offset, length, type, refcount, condition variables, proxy state, and waiter flags.
- Declares init/fini, enter/exit, and range reduction.

Main dependencies and interactions:
- `znode_t` embeds a `rangelock_t`.
- Used by read/write/truncate paths described in `zfs_znode.h`.

Implementation notes:
- The structure supports coalesced range locks and waiting readers/writers.
