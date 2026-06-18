# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4.h

Public ext4srv API header. It defines mountpoint, lock, file, directory entry, directory handle, mount statistics, and all public mount, cache, file, metadata, symlink, special-file, and directory operations.

Key behavior:
- `ext4_mountpoint` aggregates mount state, optional OS locks, core `ext4_fs`, JBD filesystem/session objects, and block cache.
- `ext4_file` tracks mountpoint, inode number, flags, size, and current position.
- `ext4_dir` embeds `ext4_file`, a reusable public directory entry, and next-entry offset.
- Declares mount/unmount, journal start/stop/recovery, stats, lock setup, superblock access, writeback toggle, and cache flush.
- Declares file remove/link/rename/open/close/truncate/read/write/seek/tell/size functions.
- Declares raw inode lookup, existence check, mode/owner/time setters and getters, symlink and mknod support, readlink, directory remove/move/mkdir/open/close/next/rewind.

Notable dependencies:
- Pulls in `ext4_types.h`, `ext4_debug.h`, `ext4_blockdev.h`, `ext4_fs.h`, and `ext4_journal.h`.
- Implemented mainly by `ext4.c`, with lower layers from the rest of ext4srv.

Research notes:
- The API blends libc-like open flags with Plan 9-style error reporting through implementation-side `werrstr`.
- Directory handle layout is used by `ext4srv.c` through a union with `ext4_file *`.
