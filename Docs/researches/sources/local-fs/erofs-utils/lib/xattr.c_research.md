# File Research: sources/local-fs/erofs-utils/lib/xattr.c

## Scope

This file implements EROFS extended attribute import, interning, shared-xattr selection and emission, inline-xattr export, read-side `getxattr`/`listxattr`, long xattr prefixes, overlayfs helper xattrs, SELinux relabel integration, Android capabilities, and xattr-manager cleanup.

## Public And Internal APIs Covered

- Manager lifecycle: `erofs_xattr_init()` and `erofs_xattr_exit()`.
- Source scanning/import: `erofs_scan_file_xattrs()`, `erofs_read_xattrs_from_disk()`, and `erofs_load_shared_xattrs_from_path()`.
- Set/remove helpers: `erofs_setxattr()`, `erofs_vfs_setxattr()`, `erofs_set_opaque_xattr()`, `erofs_clear_opaque_xattr()`, and `erofs_set_origin_xattr()`.
- Layout preparation/export: `erofs_prepare_xattr_ibody()`, `erofs_xattr_flush_name_prefixes()`, and `erofs_export_xattr_ibody()`.
- Read-side queries: `erofs_getxattr()` and `erofs_listxattr()`.
- Prefix APIs: `erofs_xattr_prefix_matches()`, `erofs_xattr_insert_name_prefix()`, `erofs_xattr_set_ishare_prefix()`, `erofs_xattr_cleanup_name_prefixes()`, `erofs_xattr_prefixes_init()`, and `erofs_xattr_prefixes_cleanup()`.

## Control Flow And Behavior

- Platform wrappers abstract Linux `llistxattr`/`lgetxattr`/`lsetxattr` and macOS `listxattr`/`getxattr`/`setxattr` no-follow variants, normalizing some missing-xattr errors.
- Xattr key/value buffers are stored as `key\0value`. `get_xattritem()` hashes key and value separately, interns duplicates in a large hash table, reference-counts users, detects short predefined prefixes, and upgrades to configured long prefixes when they match.
- File scanning lists all source xattr names, skips labels that will be overridden by SELinux relabeling, ignores inaccessible xattrs, interns readable xattrs, appends inode references, and optionally adds a generated SELinux label.
- `erofs_setxattr()` constructs a key from a short or long-prefix index plus a caller name, interns the key/value, and attaches it to the inode. VFS-style setting uses hidden/raw prefix index zero.
- Overlay helper functions add/remove `trusted.overlay.opaque` and add a zero-length `trusted.overlay.origin`; disk re-read also maps these xattrs into inode `opaque` and `whiteouts` flags.
- Android capability support emits `security.capability` from `inode->capabilities` when built with Android support.
- Shared-xattr loading recursively scans a directory tree to count all xattr occurrences, promotes entries above `inlinexattr_tolerance`, sorts shared entries for deterministic layout, writes them into an XATTR allocation, assigns shared ids, and records `sbi->xattr_blkaddr`.
- Inline xattr preparation computes `inode->xattr_isize`, replacing shareable entries with shared-id array slots up to `UCHAR_MAX`; optional `noroom` enforces an existing target size.
- Long name prefixes can be flushed in plain metadata, metabox metadata, or packed-file/fragments area depending on feature configuration. The superblock records prefix start/count and relevant feature bits.
- `erofs_export_xattr_ibody()` emits the ibody header, optional xattr name bloom-style filter, shared-id array, and inline xattr entries, while dropping inode references and item references as it consumes them.
- Read-side initialization parses an inode’s xattr ibody header and shared-id array lazily. `erofs_getxattr()` and `erofs_listxattr()` iterate inline entries first, then shared entries, handling long-prefix infixes and entries crossing block boundaries.
- `erofs_xattr_prefixes_init()` reads long-prefix records from plain metadata, packed inode, or metabox metadata, depending on feature flags and nids.

## State And Data Structures

- `struct erofs_xattrmgr` owns the intern hash table and linked list of selected shared xattrs.
- `struct erofs_xattritem` carries key/value pointer, key/value lengths, hashes, refcount, shared id, short base index, selected prefix index, and prefix length.
- `struct erofs_inode_xattr_node` links interned items into an inode’s xattr list.
- Global `ea_name_prefixes` and `ea_prefix_count` store mkfs-configured long prefixes.
- Read-side `struct erofs_xattr_iter` carries metadata-buffer cursor state, output buffer state, and lookup key state.

## Dependencies

- EROFS list, xattr format, importer parameters, cache/metabox/fragments, private config, and xxhash helpers.
- Optional Linux/macOS xattr syscalls, optional libselinux, optional Android capability definitions.

## Risks And Invariants

- Key/value length arithmetic includes the trailing key NUL; miscomputing `EROFS_XATTR_KSIZE` or prefix lengths corrupts on-disk xattr entries.
- Shared xattr ids are expressed in 4-byte units relative to `xattr_blkaddr`; offset overflow is guarded when flushing prefixes but shared xattr size still depends on buffer allocation and block placement.
- Long-prefix indexes are limited to 0x80 entries and names to `UINT8_MAX`; invalid on-disk indexes are ignored or return no data.
- Read-side iterators validate entry sizes against remaining ibody bytes and return `-EFSCORRUPTED` for overrun.
- `erofs_export_xattr_ibody()` consumes and frees the inode xattr list, so callers must treat export as a destructive flush step.
