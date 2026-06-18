# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/lofs_node.h

This header defines loopback filesystem per-vnode lnode state.

Node model:
- `lnode_t` stores hash-chain linkage, real vnode pointer, looping flags, and placeholder loopback vnode pointer.
- The lnode is the client-side “inode” for a loopback file.

Flags:
- `LO_LOOPING` indicates detected loopback recursion.
- `LO_AUTOLOOP` indicates autonode loop detection.
- `LOF_FORCE` forces creation of a new lnode when passed to `makelonode()`.

Conversions:
- `ltov()` maps lnode to loopback vnode.
- `vtol()` maps vnode to lnode.
- `realvp()` maps a loopback vnode to the underlying real vnode.

Kernel API:
- `makelonode()` creates or finds an lnode for a real vnode and mount.
- `freelonode()` frees an lnode.

Dependencies and relationships:
- Includes `lofs_info.h` for mount-level state.
- The lnode hash table is managed per mount via `loinfo`.
