# File Research: sources/os/bsd/freebsd-src/sys/sys/lockf.h

Defines kernel byte-range file lock state for POSIX/flock-style advisory locking.

Key content:
- `struct lockf_entry` represents one byte-range lock request or active lock, including semantics flags, lock type, range, owner, vnode, async callback, graph edges, and references.
- `struct lockf_edge` links blocked pending locks to active or older pending locks, forming a dependency graph.
- `struct lockf` tracks lock state for a vnode/file: active lock list, pending lock list, sx lock, and thread count.
- Lists are ordered by lock start for active locks; pending locks are newer-first and include edges for blocking/fairness.
- Extra implementation flag `F_INTR` marks locks interrupted by purge.
- Declares APIs: `lf_advlock`, `lf_advlockasync`, `lf_purgelocks`, lock iteration by sysid/vnode, lock counting, and remote system clearing.

Research relevance:
- This is the kernel structure behind VFS advisory record locks.
- Filesystems embed or reference `struct lockf *` in private vnode/node state to support `VOP_ADVLOCK`.
- The graph model is relevant to deadlock/fairness analysis for NFS and local filesystems.

Cautions:
- Field comments specify distinct locks: vnode interlock, per-state sx lock, global lock-state lock, and constant-after-allocation fields.
- Correct lifecycle depends on `ls_threads` deferring free while users may sleep.
