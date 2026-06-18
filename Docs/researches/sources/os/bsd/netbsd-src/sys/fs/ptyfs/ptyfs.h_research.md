# File Research: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs.h

Defines ptyfs node types, mount arguments, in-memory node/mount state, and kernel helper prototypes.

Key contents:
- `ptyfstype` enum:
  - `PTYFSpts` for slave side.
  - `PTYFSptc` for controlling side.
  - `PTYFSroot` for filesystem root.
- `struct ptyfskey`:
  - Vnode-cache key using node type and pty index.
- `struct ptyfsnode`:
  - Hash linkage, key, file id, timestamp status, ownership/mode/flags, and timestamps.
- `struct ptyfsmount`:
  - Mount lock, global mount-list linkage, mount pointer, gid/mode/flags, and active-pty bitmap.
- `struct ptyfs_args`:
  - Versioned mount args containing gid, mode, and flags.
- Macros:
  - File-number generation, device construction, timestamp update, mount/node casts.
- Kernel prototypes:
  - Active pty bitmap operations.
  - Vnode allocation.
  - Hash lifecycle and node lookup.
  - Timestamp update and root lookup.
  - Extern declarations for vnode ops and VFS ops.

Role:
- Shared header for ptyfs VFS operations, subroutines, and vnode layer.
