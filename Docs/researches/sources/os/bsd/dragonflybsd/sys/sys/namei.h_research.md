# File Research: sources/os/bsd/dragonflybsd/sys/sys/namei.h

Legacy namei component lookup definitions retained for VOP lookup compatibility.

Key responsibilities:
- Defines `struct componentname`, carrying operation, flags, thread, credentials, component pointer/length, consumed characters, cache timeout, and NFS collision vnode.
- Defines kernel namei operation constants for lookup, create, delete, and rename.
- Defines selected component-name flags for parent locking, following symlinks, read-only semantics, NFS `notvp` check, dot-dot, whiteouts, parent unlock, and cache timeout.
- Defines modifier and parameter masks.
- Declares `varsym_enable` and `relookup()`.

Important behavior:
- Many historical flags are commented out, suggesting DragonFly has shifted much path walking into `nlookup`/namecache while preserving selected VOP-facing bits.
- `componentname` is shared between lookup and commit routines.

Dependencies:
- Includes `queue.h`.
- Kernel includes `thread.h`, `proc.h`, and `nchstats.h`.

Notable risks:
- This header is an interop layer with legacy VFS lookup contracts; flag compatibility matters.
- Comments and masks include holes for removed/unused flags, so adding new bits requires care.
