# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_fha.c

This implements NFS File Handle Affinity scheduling. It steers NFS server requests to service threads based on file handle and, for reads/writes, file offset locality.

Key contents:
- `fha_init()` initializes hash-slot locks, default controls, tunables, and runtime sysctls.
- `fha_uninit()` frees sysctl context and destroys hash locks.
- `fha_extract_info()` uses callback functions to parse the RPC request, realign mbufs, extract file handle, offset, and lock type.
- Maintains hash entries keyed by file handle, with per-file lists of active service threads and counts of read/write and exclusive operations.
- `fha_hash_entry_choose_thread()` prefers an existing thread with nearby offset locality, falls back to the lowest-load thread, or adds the current thread if under `max_nfsds_per_fh`.
- `fha_assign()` performs assignment for NFS program requests for v2/v3 only; non-NFS and disabled cases stay on the current thread.
- `fha_nd_complete()` decrements counts and removes thread/file-handle entries once idle.
- `fhe_stats_sysctl()` emits a text snapshot of active FHA state.

Important dependencies:
- Version-specific parsing is provided through callbacks from the server integration layer.
- Uses RPC service thread scratch fields `st_p2`, `st_p3` and request fields `rq_p1`, `rq_p2`, `rq_p3`.

Risks and notes:
- Correctness depends on every assigned request calling `fha_nd_complete()`.
- The hash entry allocation path allocates a candidate entry before locking, then destroys it if an entry already exists.
