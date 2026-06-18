# File Research: sources/local-fs/erofs-utils/lib/importer.c

This file is the high-level importer lifecycle coordinator for mkfs/rebuild flows. It presets importer parameters, performs one-time global initialization, initializes per-filesystem subsystems, flushes pending filesystem state, and tears down importer-managed metadata.

Key functions:
- `erofs_importer_preset()` fills conservative defaults: fixed uid/gid disabled, `fsalignblks = 1`, build time unset, compressed extent size unspecified.
- `erofs_importer_global_init()` lazily initializes the inode manager under `erofs_importer_global_mutex`.
- `erofs_importer_init()` initializes xattrs, compression, packed-file support, metadata managers, optional fragment dedupe, 48-bit mode for omitted dot entries, and build timestamp fields.
- `erofs_importer_flush_all()` flushes metabox content, packed inode data, metadata zones, writes the device table, flushes all non-superblock buffers, and fixes up the root inode.
- `erofs_importer_exit()` exits dedupe, metadata, and packed-file facilities.

Important behavior:
- Packed file support is enabled not only for fragments but also extra EA name prefixes and compressed directories.
- `build_time` handling differs for 48-bit mode: epoch may be adjusted so the 32-bit build time field remains bounded.
- Flush order matters: metabox and packed inode data are finalized before buffer flush and root inode fixup.

Dependencies:
- `erofs_xattr_init`, `z_erofs_compress_init`, `erofs_packedfile_init`, `erofs_metadata_init`, `z_erofs_dedupe_ext_init`, `erofs_metabox_iflush`, `erofs_metazone_flush`, `erofs_bflush`, `erofs_fixup_root_inode`.

Risks / notes:
- Init failure reports the subsystem name, but already-initialized subsystems are not unwound here; callers must pair successful initialization with exit.
- Global inode manager initialization is process-wide and intentionally guarded for repeated importer creation.
