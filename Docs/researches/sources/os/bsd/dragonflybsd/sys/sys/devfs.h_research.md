# File Research: sources/os/bsd/dragonflybsd/sys/sys/devfs.h

DragonFly devfs node, mount, message, cloning, alias, and kernel API header.

Key responsibilities:
- Defines devfs node types and lightweight dirent/fid structures.
- Defines `struct devfs_node` with cdev, mount, dirent, vnode, parent, type, children, readdir cookie state, link/symlink state, ownership/perms/flags, timestamps, and child list.
- Defines kernel mount data, orphan tracking, clone handlers, aliases, dev_ops ref records, and a large `devfs_msg` union for asynchronous core operations.
- Defines devfs message IDs for device create/destroy, mount add/del, clone handler, find, alias, rules, scans, related destruction, inode-to-vnode, and sync.
- Defines node flags for linked/user-created/orphaned/cloned/hidden/invisible/pty/destroyed/rule-created/rule-hidden/link-wait states.
- Defines clone bitmap helpers and extensive kernel APIs for node allocation/free/link/unlink, perms, GC, message sending, mount registration, node/path resolution, device creation/destruction, aliasing, rules, scans, cdev private data, and wildcard matching.
- Defines public mount flags and `struct devfs_mount_info`.

Dependencies:
- Kernel paths include queue, lock, conf, msgport, dirent, device, and ucred headers.
- Tightly coupled to vnode, mount, cdev/dev_ops, kqueue, and LWKT messaging.

Notable risks:
- Node accessibility has two different hiding concepts: inaccessible hidden nodes and readdir-invisible nodes.
- The message union carries many pointer types and depends on correct message ID interpretation.
- `DEVFS_DEFAULT_MODE` macro includes a trailing semicolon in its definition, which is style-sensitive in expressions.
