# File Research: sources/os/linux/linux/fs/xfs/scrub/tempexch.h

This header declares the temporary-file exchange wrapper used by online repair code when `CONFIG_XFS_ONLINE_REPAIR` is enabled.

Key type:
- `struct xrep_tempexch`: wraps `struct xfs_exchmaps_req`.

Declared functions:
- `xrep_tempexch_trans_reserve`: prepare exchange request and reserve resources in an existing transaction.
- `xrep_tempexch_trans_alloc`: allocate a fresh transaction, lock inodes, join them, and reserve resources.
- `xrep_tempexch_contents`: perform the mapping exchange and finish deferred work.

Scope:
- Only declared for online repair builds.
- Used by file-based metadata repairs such as symlink and realtime summary repair to atomically commit rebuilt contents staged in a tempfile.

Risk notes:
- The wrapper centralizes exchange-map request construction and transaction reservation, which keeps repair callers from open-coding low-level `xfs_exchmaps_req` setup.
