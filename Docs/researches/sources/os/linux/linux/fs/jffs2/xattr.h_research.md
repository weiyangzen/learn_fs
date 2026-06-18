# File Research: sources/os/linux/linux/fs/jffs2/xattr.h

## Purpose
Declares JFFS2 xattr in-memory structures, state flags, helper macros, subsystem entry points, VFS xattr handlers, and no-op stubs for builds without xattr/security support.

## Main Definitions
- `JFFS2_XFLAGS_HOT`, `JFFS2_XFLAGS_BIND`, `JFFS2_XFLAGS_DEAD`, and `JFFS2_XFLAGS_INVALID` define datum cache/reclaim/corruption state.
- `struct jffs2_xattr_datum` stores raw-node chain pointer, prefix, cache-list link, refcount, xid/version, CRC/hash, name, and value.
- `struct jffs2_xattr_ref` stores raw-node chain pointer, xref sequence, inode cache or scanned inode number, xattr datum or scanned xid, and inode-local next pointer.
- `XREF_DELETE_MARKER` is the low xseqno bit used to represent deletion records.
- `is_xattr_ref_dead()` tests whether an xref sequence carries the delete marker.

## Exported Interfaces
- Subsystem lifecycle: `jffs2_init_xattr_subsystem()`, `jffs2_build_xattr_subsystem()`, `jffs2_clear_xattr_subsystem()`.
- Scan/build support: `jffs2_setup_xattr_datum()`.
- Inode lifecycle: `jffs2_xattr_do_crccheck_inode()`, `jffs2_xattr_delete_inode()`, `jffs2_xattr_free_inode()`.
- GC support: `jffs2_garbage_collect_xattr_datum()`, `jffs2_garbage_collect_xattr_ref()`, `jffs2_verify_xattr()`, release helpers.
- VFS operations: `do_jffs2_getxattr()`, `do_jffs2_setxattr()`, `jffs2_listxattr()`.
- Handler exports: `jffs2_xattr_handlers`, `jffs2_user_xattr_handler`, `jffs2_trusted_xattr_handler`, and optional security handler/init.

## Compile-Time Behavior
- Under `CONFIG_JFFS2_FS_XATTR`, all xattr interfaces are real functions.
- Without `CONFIG_JFFS2_FS_XATTR`, the subsystem lifecycle and inode hooks become no-ops, `jffs2_verify_xattr()` returns success, and VFS handler/list hooks are `NULL`.
- Under `CONFIG_JFFS2_FS_SECURITY`, security xattr initialization and handler declarations are enabled; otherwise `jffs2_init_security()` is a no-op.

## Dependencies
- Includes Linux `xattr.h` and `list.h`.
- Expects `struct jffs2_sb_info`, `struct jffs2_inode_cache`, and raw node types from surrounding JFFS2 headers.
