# File Research: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs_subr.c

Implements ptyfs node allocation/cache helpers and active-pty tracking.

Key points:
- `ptyfs_allocvp()` creates vnode-cache keys from type and pty number and calls `vcache_get()`.
- Hash lifecycle:
  - `ptyfs_hashinit()` creates a small global hash table and lock.
  - `ptyfs_hashdone()` destroys them.
- `ptyfs_get_node()` returns or allocates a `ptyfsnode` by type/pty.
  - Initializes unique file number, permissions, ownership, status flags, timestamps, and hash linkage.
  - Root gets directory-style read/execute permissions; pty nodes get character-device-style read/write permissions.
- Active pty bitmap:
  - `ptyfs_set_active()` grows the per-mount bitmap as needed and marks a pty active.
  - `ptyfs_clr_active()` clears an active pty if present.
  - `ptyfs_next_active()` scans for the next active pty at or after a given index.

Risk/notes:
- Comment documents a small race where duplicate unused list entries may be inserted when opening master side concurrently through multiple mount points.
