# File Research: sources/local-fs/erofs-utils/lib/liberofs_metabox.h

This header declares metadata-zone/metabox support.

Definitions:
- `EROFS_META_NEW_ADDR` marks a not-yet-placed metadata zone.
- `erofs_metabox_identifier` / `EROFS_METABOX_INODE` identify the generated metabox inode by pointer identity.
- `erofs_is_metabox_inode()` checks that special source path.
- `erofs_has_meta_zone()` checks whether metadata-zone support is active or pending.

API:
- `erofs_metadata_init()`, `erofs_metadata_exit()`
- `erofs_metadata_bmgr(struct erofs_sb_info *sbi, bool mbox)`
- `erofs_metabox_iflush(struct erofs_importer *im)`
- `erofs_metazone_flush(struct erofs_sb_info *sbi)`

Known users:
- `importer.c` initializes metadata managers and flushes metabox/metazone data.
- `inode.c` places ordinary inodes in metabox when available, and writes directory data into metadata zone when configured.
- `metabox.c` implements the API.

Risk / note:
- Special metabox inode identity is pointer-based, so callers must use the exported identifier, not a copied string.
