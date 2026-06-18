# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_conf.c

This file locates and mounts the root filesystem during boot and provides helper routines for root device selection, interactive root prompts, devfs mounting, and reporting the real root mount string.

Global root state:
- Defines `rootvnode` and `rootnch`.
- Defines `M_MOUNT` allocation type for mount structures.
- Maintains legacy `rootdevnames[2]` candidates and `rootdev`.
- Registers `vfs_mountroot` via `SYSINIT` at `SI_SUB_MOUNT_ROOT`.

Root mount selection order in `vfs_mountroot`:
- Synchronizes device probing with `sync_devs` and sleeps for tunable `vfs.root.wakedelay`.
- Tries compiled-in `ROOTDEVNAME` when boot flags request default root.
- Prompts manually for `RB_DFLTROOT` or `RB_ASKNAME`.
- Tries built-in CD-ROM candidates under `RB_CDROM`.
- Tries loader/environment `vfs.root.mountfrom`.
- Tries a preexisting `rootdev` value.
- Tries legacy machine-dependent `rootdevnames`.
- Falls back to compiled default and finally manual prompt.
- Panics if all attempts fail.

`vfs_mountroot_try` handles one or more semicolon-separated root specifications in `<vfsname>:<device>` form. It allocates a root mount through `vfs_rootmountalloc`, marks it `MNT_ROOTFS`, tries to set `rootdev` for non-HAMMER filesystems, clears read-only for memory disks, and calls `VFS_MOUNT`.

On successful root mount, it:
- Inserts the mount first in the mount list.
- Initializes system time from root fs timestamp with `inittodr`.
- Obtains `/` through `VFS_ROOT`.
- Allocates a root namecache handle if the mount did not provide one.
- Sets current process vnode cwd/root fields and namecache cwd/root fields.
- Installs root vnode/namecache through `vfs_cache_setroot`.
- Allocates a syncer vnode if needed.
- Calls `VFS_START`.

On failure, it stops the syncer thread, unbusies and frees the mount, and reports the mount error.

`vfs_mountroot_devfs` mounts `devfs` on `/dev` after root is mounted. It optionally prefixes `/dev` with `init_chroot`, resolves the path with `nlookup`, validates that the target is a directory vnode, allocates and initializes a devfs mount, calls `VFS_MOUNT`, creates a mount-root namecache if needed, marks the mount-on ncp with `NCF_ISMOUNTPT`, inserts the mount after root, allocates a syncer vnode, and starts the filesystem. Its failure path explicitly unwinds vnode ops, syncer state, mount refs, and namecache refs.

Manual root prompting:
- `vfs_mountroot_ask` prints supported syntax, lets the user list disk devices with `?`, panic, abort, or try a mount string.
- `get_line` polls the console, supports enter, backspace/delete, `#` erase-one-character behavior, and Ctrl-U line kill.

Device helpers:
- `kgetdiskbyname` strips `/dev/` if present and uses devfs lookup to return a `cdev_t`.
- `setrootbyname` updates global `rootdev` from a disk name, clearing it on failure to avoid stale retries.
- With DDB enabled, `show disk/<name>` reports the matching `cdev_t`.

Sysctl:
- `vfs.real_root` reports environment variable `vfs.root.realroot` or an empty string.

Notable dependencies include boot flags, kernel environment variables, devfs, nlookup/namecache, mount list operations, VFS mount/root/start hooks, vnode locking, syncer vnode allocation, and console polling.

Implementation risks for future changes:
- Root mount success wires together vnode cwd/root state and namecache cwd/root state; these must stay consistent.
- Devfs mount failure cleanup is manual and order-sensitive.
- `vfs_mountroot_try` parses fixed-size buffers with kernel `scanf` patterns; changing accepted syntax should preserve bounds and semicolon iteration.
- HAMMER and HAMMER2 intentionally skip `setrootbyname`, reflecting filesystem-specific root-device semantics.
