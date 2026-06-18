# File Research: sources/os/linux/linux-stable/fs/jffs2/xattr.c

Complete JFFS2 extended-attribute engine for storing xattr name/value data (`xdatum`) and inode-to-xattr references (`xref`) as flash nodes. It handles lazy verification/loading after mount, deduplication of identical xattr data, VFS list/get/set operations, and GC relocation/release paths.

Key flows:
- `xattr_datum_hashkey()`, `load_xattr_datum()`, `save_xattr_datum()`, and `create_xattr_datum()` manage cached xattr data, CRC verification, hash indexing, flash writes, and memory pressure reclamation.
- `verify_xattr_ref()`, `save_xattr_ref()`, `create_xattr_ref()`, and `delete_xattr_ref()` manage xref nodes and sequence-number delete markers.
- `jffs2_build_xattr_subsystem()` merges duplicate refs, binds refs to inode caches and xdata, and classifies dead/orphan/unchecked records during mount build.
- `jffs2_listxattr()`, `do_jffs2_getxattr()`, and `do_jffs2_setxattr()` implement VFS xattr semantics, including create/replace/delete behavior and reserve-space/complete-reservation pairing.
- GC entry points `jffs2_garbage_collect_xattr_datum()` and `jffs2_garbage_collect_xattr_ref()` rewrite live xattr nodes and obsolete old raw refs.

Important state/locking:
- `c->xattr_sem` serializes most xattr subsystem mutations.
- `c->erase_completion_lock` protects raw-node chains and dead lists.
- Positive `JFFS2_XATTR_IS_CORRUPTED` return means unrecoverable corruption requiring node/ref deletion; negative errors are retryable/recoverable I/O or allocation failures.
- The cache uses `JFFS2_XFLAGS_HOT` and `JFFS2_XFLAGS_BIND` to avoid reclaiming active data while scanning/comparing duplicate names.

Integration points:
- Uses raw flash I/O (`jffs2_flash_read`, `jffs2_flash_write`, `jffs2_flash_writev`), reservation APIs, summary sizes, inode cache xref chains, CRC32, and xattr handler visibility checks.
- Exposes `jffs2_xattr_handlers[]` for user, trusted, optional security, and optional POSIX ACL prefixes.

Risk notes:
- Correctness depends on raw-node chain invariants where `next_in_ino` terminates at the owning object sentinel.
- Error handling around two-stage setxattr is delicate: xdatum write succeeds before xref reservation/write, so rollback must unreference the datum on xref failure.
- Duplicate-name cleanup chooses newest `xseqno`; any sequence-number ordering bug could expose stale attributes.
