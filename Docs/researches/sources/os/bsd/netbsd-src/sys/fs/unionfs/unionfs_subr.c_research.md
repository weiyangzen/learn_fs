# File Research: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs_subr.c

Read completely: 937 lines.

Provides support routines for the newer `unionfs`: union vnode creation/removal, per-thread open-status tracking, upper attribute policy, relookup helpers, shadow directory and whiteout creation, copy-up, rmdir emptiness checks, and diagnostic accessors.

`unionfs_nodeget()` creates a unionfs vnode using `vcache_get()` keyed by the active underlying vnode, references upper/lower/parent vnodes, saves the final component path when available, sets vnode type, initializes UVM size to zero, and marks the root vnode. `unionfs_noderem()` clears underlying vnode pointers, releases references, frees saved path and all node-status records, and frees the node. `unionfs_get_node_status()` and `unionfs_tryrem_node_status()` maintain per-PID/LWP open and readdir state while the unionfs vnode is exclusively locked.

Attribute creation is policy-driven. `unionfs_create_uppervattr_core()` copies lower attributes transparently, applies masquerade ownership/mode rules, or uses traditional mount-user ownership and current umask. `unionfs_relookup()` and the create/delete/rename wrappers rebuild namei state against the upper directory after copy-up or before upper-layer operations.

Copy-up helpers create an upper shadow file with `unionfs_vn_create_on_upper()`, copy data in `MAXBSIZE` chunks with `unionfs_copyfile_core()` when requested, restore attributes, and update the unionfs node to point at the new upper vnode. `unionfs_mkshadowdir()` creates upper shadow directories and updates the node, while `unionfs_mkwhiteout()` prepares a whiteout lookup path but in this NetBSD version returns after relookup without issuing `VOP_WHITEOUT(CREATE)` directly. `unionfs_check_rmdir()` reads lower directory entries and treats entries hidden by upper entries or whiteouts as removable.

Risks and notes: `unionfs_node_update()` updates only `un_uppervp` and assumes the lower vnode is exclusively locked; `unionfs_vn_create_on_upper()` panics if `un_path` is absent; shadow-directory uid/gid reset is attempted with `lwp0.l_cred` and explicitly questioned in a comment; `unionfs_mkwhiteout()` appears incomplete compared with the legacy union helper because it does not call `VOP_WHITEOUT()` after successful relookup.
