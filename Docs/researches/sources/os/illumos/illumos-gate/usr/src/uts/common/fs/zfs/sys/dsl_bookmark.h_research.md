# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_bookmark.h

Read status: complete, 69 lines.

Purpose: DSL bookmark physical format and management interface.

Key structures and APIs:
- `zfs_bookmark_phys_t` stores bookmarked dataset GUID, creation TXG/time, redaction-related reserved fields, referenced/compressed/uncompressed byte stats, freed-before-next-snap stats, and raw-send IV-set GUID.
- Physical size constants: `BOOKMARK_PHYS_SIZE_V1`, `BOOKMARK_PHYS_SIZE_V2`.
- APIs: `dsl_bookmark_create()`, `dsl_get_bookmarks()`, `dsl_get_bookmarks_impl()`, `dsl_bookmark_destroy()`, `dsl_bookmark_lookup()`.

Dependencies: ZFS context, DSL dataset.

Research notes:
- Bookmark format already reserves fields for redacted send/receive and raw sends.
- Stored as on-disk ZAP entries.
