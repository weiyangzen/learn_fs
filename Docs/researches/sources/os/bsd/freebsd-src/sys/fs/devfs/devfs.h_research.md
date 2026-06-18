# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs.h

Read completely: 215 lines.

Purpose: public/private devfs definitions for rules, dirents, mount state, ioctl ABI, and kernel helper prototypes.

Key rule definitions:
- `DEVFS_MAGIC` validates rule ABI payloads.
- `devfs_rnum`, `devfs_rsnum`, and `devfs_rid` identify rules and rulesets; `rid2rsn()`, `rid2rn()`, and `mkrid()` pack/unpack IDs.
- `struct devfs_rule` is pointer-free and shared with userland. It includes condition flags (`DRC_DSWFLAGS`, `DRC_PATHPTRN`) and action flags (`DRA_BACTS`, `DRA_UID`, `DRA_GID`, `DRA_MODE`, `DRA_INCSET`).
- Rule ioctls cover add/delete/apply/get-next and ruleset use/apply/get-next.

Key kernel structures:
- `struct devfs_dirent` models synthetic `/dev` tree entries: cdev pointer, inode, flags, embedded dirent, children list, parent, permissions, labels, timestamps, vnode, symlink target, and use count.
- `struct devfs_mount` tracks mount index, root dirent, generation, hold count, lock, and active ruleset.

Key prototypes:
- Rule application/cleanup/ioctl helpers.
- Vnode allocation, fqpn generation, deletion, population, cleanup, unmount finalization.
- Directory creation/find helpers and controlling-tty reference helpers.

Research notes:
- `DE_WHITEOUT`, `DE_COVERED`, and `DE_USER` are important for rules and user-created symlink overlay behavior.
- `DEVFS_ROOTINO` is fixed at 2.
