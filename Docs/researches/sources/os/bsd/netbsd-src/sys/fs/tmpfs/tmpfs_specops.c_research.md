# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_specops.c

Read completely: 119 lines.

This defines the tmpfs vnode operation vector for block and character special devices. It combines `GENFS_SPECOP_ENTRIES` with tmpfs metadata operations and wrappers around specfs close/read/write.

`tmpfs_spec_read` updates atime before delegating to `spec_vnodeop_p`; `tmpfs_spec_write` updates mtime before delegating. `tmpfs_spec_close` delegates directly to specfs close.

Important interactions: `tmpfs_init_vnode` selects this vector for `VBLK` and `VCHR` and calls `spec_node_init`.

Security/reliability notes: device I/O semantics remain in specfs; tmpfs only maintains filesystem metadata around those operations.
