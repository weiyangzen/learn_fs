# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/9fs.h

Read fully: 219 lines, 8290 bytes. SHA-256 prefix: `a5e4551be7db6fdd`.

This header defines FreeBSD-side 9FS mount arguments and kernel-facing state, derived from old BSD NFS headers.

Key content:
- Mount option flags such as `U9FSMNT_SOFT`, `U9FSMNT_INT`, `U9FSMNT_KERB`, and `U9FSMNT_READAHEAD`.
- `struct p9user`, mapping Unix UIDs to Plan 9 names.
- `struct u9fs_args`, passed to `mount()`, containing server socket info, sizes, hostname, auth server info, username, DES key, and user mappings.
- `struct u9fsnode`, a vnode-private node with cached attributes, mode cache, fid pointer, vnode pointer, lock/error flags, and legacy disabled NFS fields.
- `struct u9fsmount`, mount-private socket and size state.
- Macros converting vnode/mount pointers to 9FS structures.

Integration: used by `mount_9fs.c` and expected by a matching FreeBSD kernel `u9fs` module.

Risk notes: much of the layout and comments are inherited from NFS and include disabled or stale fields.
