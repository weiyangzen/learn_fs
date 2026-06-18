# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null_vfsops.c

This file implements nullfs VFS operations. Mount resolves the target path via namecache, gets the lower root vnode, allocates `struct null_mount`, installs vnode ops, stores a held root vnode reference, adjusts mount flags inherited from the lower filesystem, and sets up namecache mount-point state for DragonFly’s lightweight stacking model.

It supports mount updates for export changes, generates a stable-ish fsid from the lower root file handle plus mount path CRC, forwards statfs/quotactl/extattr/namecache-generation operations to the lower filesystem, and implements NFS export checks against nullfs-local export state.

Unmount releases the held root vnode and frees mount state. `nullfs_modifying()` rejects writes on a read-only nullfs mount and otherwise forwards modification checks to the lower filesystem.

Research notes: comments emphasize that when stacking nullfs over nullfs, it must avoid endless recursion by resolving the actual lower filesystem mount. The mount is registered as loopback and MPSAFE with no syncer thread.
