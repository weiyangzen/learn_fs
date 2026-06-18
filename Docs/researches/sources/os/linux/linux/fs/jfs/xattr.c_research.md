# File Research: sources/os/linux/linux/fs/jfs/xattr.c

JFS extended-attribute service for on-disk EA lists, inline/extent storage, Linux xattr handlers, and security initialization.

Key responsibilities:
- Defines the JFS EA list format and `ea_buffer` state for inline, extent, newly allocated, and malloc-backed buffers.
- Maps unknown on-disk namespaces to Linux-visible `os2.` names while preserving known `system.`, `user.`, `security.`, and `trusted.` prefixes.
- Writes EA lists inline when possible through `ea_write_inline()`, otherwise allocates extent blocks and writes through metapages in `ea_write()`.
- Reads inline or extent-backed EA lists through `ea_read_inline()` and `ea_read()`.
- Loads and optionally expands an EA list through `ea_get()`, validating recorded list size against inode EA descriptors.
- Releases or commits EA buffers through `ea_release()` and `ea_put()`, updating transaction EA locks and freeing old quota blocks.
- Implements `__jfs_setxattr()`, including create/replace semantics, deletion by null value, list compaction, value-size checks, and list-size recalculation.
- Implements `__jfs_getxattr()` and `jfs_listxattr()`, including corrupted-entry bounds checks and trusted-name filtering.
- Exposes xattr handlers for `os2.`, `user.`, `security.`, and `trusted.` namespaces.
- Implements security xattr initialization under `CONFIG_JFS_SECURITY`.

Important interactions:
- Uses inode EA descriptor `JFS_IP(inode)->ea`, inline EA area, `INLINEEA`, and `xattr_sem`.
- Uses block allocator and quota helpers `dbAlloc()`, `dbFree()`, `dquot_alloc_block()`, and `dquot_free_block()`.
- Uses metapage I/O helpers `get_metapage()`, `read_metapage()`, `flush_metapage()`, `release_metapage()`, and `discard_metapage()`.
- Uses transaction helper `txEA()` to log replacement/removal of EA descriptors.
- Integrates with VFS xattr handler dispatch and LSM `security_inode_init_security()`.

Invariants and risks:
- EA list size is stored on disk and must match `DXD` size; mismatch is treated as corruption.
- EA value length is stored in 16 bits, so values at or above `USHRT_MAX` return `-E2BIG`.
- Buffer growth in `__jfs_setxattr()` may release and reacquire storage, so pointer state is rebuilt with a second pass.
- Newly allocated extent buffers must free both quota and blocks if validation or readback fails.
- Inline EA storage competes with xtree root expansion; `INLINEEA` flag transitions must remain consistent.
