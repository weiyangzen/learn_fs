# File Research: sources/os/linux/linux/fs/remap_range.c

Generic VFS helpers for reflink/clone and dedupe range operations.

Key responsibilities:
- `generic_remap_checks()` validates alignment, range overflow, EOF bounds, write limits, same-file overlap, and shortening rules.
- `remap_verify_area()` validates range sign/overflow and checks LSM plus fsnotify area permissions.
- `generic_remap_check_len()` handles partial EOF block rules for clone and dedupe.
- Dedupe data comparison:
  - `vfs_dedupe_get_folio()`
  - `vfs_lock_two_folios()`
  - `vfs_unlock_two_folios()`
  - `vfs_dedupe_file_range_compare()`
- `__generic_remap_file_range_prep()` performs common clone/dedupe preparation:
  - rejects immutable output and swapfiles,
  - rejects unsupported inode types,
  - handles zero-length clone-to-EOF behavior,
  - waits for direct IO,
  - writes back dirty page-cache ranges,
  - compares data for dedupe,
  - calls `file_modified()` for non-dedupe writes.
- `generic_remap_file_range_prep()` wraps the prep helper without DAX ops.
- `vfs_clone_file_range()` validates same-superblock clone and invokes `remap_file_range`.
- `may_dedupe_file()` checks whether the caller may dedupe into a destination.
- `vfs_dedupe_file_range_one()` dedupes one destination file/range.
- `vfs_dedupe_file_range()` handles multi-destination dedupe requests and fills per-destination statuses.

Important behavior:
- Clone requires same superblock.
- Dedupe also requires same superblock and readable source, and the destination must be writable or owned/permitted unless caller has `CAP_SYS_ADMIN`.
- Non-DAX dedupe comparison reads folios, locks them in stable order, checks mappings/uptodate state, flushes dcache, and `memcmp`s page-sized chunks.
- DAX dedupe comparison is delegated if DAX read ops are provided.
- Single dedupe requests are capped to 1 GiB.
- Per-destination dedupe reports `FILE_DEDUPE_RANGE_DIFFERS` when data comparison fails with `-EBADE`.

Research notes:
- Filesystems provide the actual remap operation through `->remap_file_range`; this file supplies common VFS safety and permission checks.
