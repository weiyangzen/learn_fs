# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/autofs.h

This header defines kernel autofs mount/node state plus the shared door/syscall interface used between the kernel and automount daemon.

Kernel mount state:
- `fninfo_t` is per-autofs-mount metadata: mount/root vnodes, RPC netconfig/address, mount path, map/subdir/key/options strings and lengths, refcount, flags, timeouts, and zone id.

Kernel node state:
- `fnnode_t` is the autofs inode equivalent. It stores name/symlink, mode/uid/gid/link count, error, node id, directory offset/size, vnode, parent/sibling/child/trigger links, action list, credential for user-relative matching, locks, timestamps, mount condition variable, traversal tracking (`fn_seen`, `fn_thread`), and global pointer.
- `autofs_globals` stores root node, node count, unmount-thread state, verbosity, zone id, daemon pid, daemon door lock, and door handle.

Locking model:
- `fn_lock` protects most per-node fields.
- `fn_rwlock` protects directory/list traversal and fields such as `fn_dirents`, `fn_next`, `fn_size`, and `fn_linkcnt`.
- Lock ordering is `fn_rwlock` before `fn_lock`.

Flags:
- `MF_INPROG`, `MF_WAITING`, `MF_LOOKUP`, `MF_ATTR_WAIT`, `MF_IK_MOUNT`, `MF_DIRECT`, `MF_TRIGGER`, `MF_THISUID_MATCH_RQD`, and `MF_MOUNTPOINT` encode ongoing daemon operations, mount style, trigger/user-relative semantics, and mountpoint state.
- `AUTOFS_MODE` and `AUTOFS_BLOCKSIZE` define default mode/block size.

Kernel helpers:
- Search, enter, make/free/disconnect nodes, wait for mounts, call daemon, trigger lookup/mount threads, unmount subtrees, shutdown zones, and logging/debug helpers.
- `AUTOFS_BLOCK_OTHERS` and `AUTOFS_UNBLOCK_OTHERS` synchronize mount/lookup operations on a node.

Door/shared ABI:
- Command ids include null, mount, unmount, readdir, lookup, srvinfo, and mntinfo.
- `autofs_door_args_t` and `autofs_door_res_t` carry command plus XDR-encoded argument/result buffers.
- Security data structures include DES and GSS client data.
- `RESTRICTED_MNTOPTS` lists mount options inherited under the `restrict` option.

Syscall:
- `enum autofssys_op` defines unmount-all and set-door operations.
- Kernel declares `autofssys()`.

Dependencies and relationships:
- Ties VFS/vnode state, RPC/XDR protocol structures, doors, zones, and automount daemon communication.
