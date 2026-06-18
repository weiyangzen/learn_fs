# File Research: sources/os/bsd/freebsd-src/sys/fs/unionfs/union.h

FreeBSD unionfs internal structure and helper declaration header.

Key responsibilities:
- Defines copy modes: traditional, transparent, and masquerade.
- Defines whiteout policy modes: always and when-needed.
- Defines `struct unionfs_mount`, carrying lower/upper mounts and root vnodes, upper registration links, copy/whiteout policy, owner/group, and mode defaults.
- Defines per-process `unionfs_node_status` open/readdir tracking.
- Defines `struct unionfs_node`, carrying upper/lower vnode references, parent union vnode, child directory vnode cache, path component, and in-progress flags.
- Provides checked conversion macros and declarations for unionfs node, copy-up, whiteout, shadow directory, relock, forwarding, and rmdir helpers.

Dependencies:
- Kernel-only header depending on FreeBSD mount, vnode, list, task, and VOP infrastructure.
- References `unionfs_vnodeops`, implemented outside this group.

Notable risks:
- Unionfs vnodes share locks with underlying vnodes; `VTOUNIONFS` and node fields must handle reclaimed/doomed vnodes carefully.
- In-progress flags require exclusive vnode locking and coordinate copy-up/lookup races.
- Path storage is used for later copy-up, so component lifetime and `ISLASTCN` handling matter.
