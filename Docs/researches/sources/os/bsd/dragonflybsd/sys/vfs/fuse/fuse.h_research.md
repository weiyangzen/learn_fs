# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse.h

Central private header for the DragonFlyBSD FUSE implementation. It includes kernel synchronization, mount, vnode, file, credential, sysctl, tree, lockf, and ABI headers; defines conversion macros; declares global vnode ops and function prototypes; and defines the main FUSE mount/node/IPC structures.

`struct fuse_mount` is the per-mount state. It tracks the DragonFly mount, backing `/dev/fuse` vnode, mount credential, kqueue list, root node, mount/ipc/inode locks, helper thread, bio queue, pending request/reply queues, RB tree of nodes, refcount, unique request counter, dead flag, unsupported-op bitset, negotiated ABI version, and max write size.

`struct fuse_node` is the incore inode/vnode state. It stores RB-tree linkage, vnode pointer, cached attributes, mount pointer, parent pointer, node lock, advisory lock state, FUSE inode number, vnode type, size, lookup count, file handle, closed marker, dirty/access/change bits, and attribute validity/size override bits.

`struct fuse_ipc` represents one userspace request/reply transaction, with request and reply buffers, queue links, refcount, unique ID, sent flag, and done flag.

Inline helpers expose request/reply headers and payloads, test/set mount death, record `ENOSYS` operations in the `nosys` mask, and mark IPC replies. `fuse_knote` sends vnode kqueue notifications.

Important dependencies: all FUSE `.c` files include this header. It imports the Linux-compatible ABI from `fuse_abi.h` and mount arguments from `fuse_mount.h`.

Notable risks or research hooks: `fuse_test_nosys` and `fuse_set_nosys` use `1 << op` against a 64-bit mask; opcodes beyond the native int shift width or above 63 need scrutiny. `INVARIANTS` is forced on unless already defined, which changes assertion behavior in this module.
