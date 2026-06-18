# File Research: sources/local-fs/xfsdump/restore/inomap.c

## Summary
Implements the restore-side inode map abstraction. It restores the on-media inode map into a housekeeping file, maps it into memory, tracks restore-needed state for non-directories, and offers range queries and iteration over inode states.

## Main Responsibilities
- Restore serialized inode-map hunks from media into the persistent `inomap` housekeeping file.
- Reopen and mmap an existing persistent inode map during resume or later restore phases.
- Store inode state in 64-inode segments with three bitplanes, supporting the `MAP_*` states from `inomap.h`.
- Mark selected non-directory inodes as restore-needed or no-restore for subtree restores.
- Answer whether any inode in an inclusive range still needs restore.
- Iterate all inodes whose state is included in a caller-supplied state mask.
- Discard inode-map bytes from media when a restore path does not need to persist them.

## Important Behavior
`inomap_restore_pers()` takes hunk count, segment count, and last inode from `content_inode_hdr_t`, creates `hkdir/inomap`, mmaps enough space, reads all hunks from the drive, translates each hunk with `xlate_hnk()`, unmaps/closes, and calls `inomap_sync_pers()`.

`inomap_sync_pers()` opens an existing `inomap`, mmaps the persistent header, then mmaps the hunk array separately. It rebuilds `nextp` pointers because persisted pointer values are not valid across process mappings.

`SEG_SET_BITS()` and `SEG_GET_BITS()` encode one 3-bit state per inode by setting or reading the low, middle, and high bitplanes in a segment.

`inomap_sanitize()` converts every `MAP_NDR_CHANGE` entry to `MAP_NDR_NOREST`, which makes later subtree selection explicitly opt non-directories back into restore.

`inomap_rst_add()` and `inomap_rst_del()` mutate a single inode between `MAP_NDR_CHANGE` and `MAP_NDR_NOREST`.

`inomap_rst_needed()` scans mapped hunks and segments to see if any inode in a requested range is `MAP_NDR_CHANGE`.

`map_getsegment()` uses binary search over the mmapped hunk array and then over a hunk’s segment array, relying on sorted, contiguous hunk storage.

## Dependencies
Depends on xfsdump media/content headers, drive read callbacks, `read_buf()`, `open_pathalloc()`, `mmap_autogrow()`, `arch_xlate`, XFS inode types, logging, and the global page-size-derived `perssz`.

## Risks
`map_getsegment()` uses unsigned `min`/`max` values with `max >= min` loops. If a search underflows `max`, the loop can misbehave; this is especially sensitive for inode values before the first hunk or segment.

`inomap_discard()` reads `tmphnkcnt` from the supplied media header but asserts the byte count against global `hnkcnt`, which may be stale or unrelated if no map was restored first.

Most corruption handling depends on assertions after reads and mmap sizing. Release builds with assertions disabled may continue after inconsistent metadata.

The persistent hunk array is trusted to be sorted and structurally valid; bad media could make binary search, `lastsegp`, or iteration assumptions unsafe.
