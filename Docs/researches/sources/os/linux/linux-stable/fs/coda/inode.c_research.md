# File Research: sources/os/linux/linux-stable/fs/coda/inode.c

This file implements Coda filesystem superblock setup, mount-context parsing, inode-cache lifecycle, and common inode attributes operations.

Key responsibilities:
- Defines `coda_super_operations` with custom inode allocation/free, eviction, `put_super`, and `statfs`.
- Manages `coda_inode_cachep` via `coda_init_inodecache()` and `coda_destroy_inodecache()`.
- Parses new mount API parameter `fd=` and legacy binary mount data to select a Coda pseudo-device minor.
- `coda_fill_super()` binds a `struct venus_comm` pseudo-device channel to the superblock, requests the root fid from Venus, creates the root inode, and installs `s_root`.
- Restricts Coda mounts to the initial PID namespace through `coda_get_tree()`.
- Implements `coda_getattr()` and `coda_setattr()` as VFS-facing wrappers around Venus revalidation/setattr upcalls.
- Provides `coda_file_inode_operations`.

Important control flow:
- Mount setup: `coda_init_fs_context()` allocates `struct coda_fs_context`, `coda_parse_param()` or `coda_parse_monolithic()` sets `idx`, `coda_get_tree()` calls `get_tree_nodev()`, and `coda_fill_super()` validates `vc_inuse`/`vc_sb`.
- On failure after assigning `vc->vc_sb`, `coda_fill_super()` clears `vc_sb` and `sb->s_fs_info` under `vc_mutex`.
- `coda_put_super()` detaches the superblock from the pseudo-device state and destroys the channel mutex.

Dependencies:
- Depends on `coda_comms[]` and pseudo-device lifecycle from `psdev.c`.
- Depends on Venus RPC helpers in `upcall.c`, including `venus_rootfid()`, `venus_setattr()`, and `venus_statfs()`.
- Depends on inode/cache helpers from other Coda files such as `coda_cnode_make()`, `coda_revalidate_inode()`, and cache invalidation helpers.

Risks and invariants:
- A pseudo-device minor can have only one mounted superblock at a time.
- Mounting is intentionally limited to the initial PID namespace.
- `coda_parse_monolithic()` preserves legacy behavior by ignoring invalid file descriptor lookup failures after validating the mount-data version.
- `coda_statfs()` deliberately returns fake capacity data when Venus statfs fails.
