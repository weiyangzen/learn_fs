# File Research: sources/local-fs/jfsutils/xpeek/fsckcbbl.c

Implements inspection and editing of JFS fsck workspace metadata, ClearBadBlockList/fsck communication records, and journal log superblock data.

Top-level commands:
- `cbblfsck(void)`: reads fsck workspace header, displays/edits the embedded `fsckcbbl_record`, writes back if changed.
- `fsckwsphdr(void)`: reads fsck workspace header, displays/edits `fsck_blk_map_hdr.hdr`, writes back if changed.
- `logsuper(void)`: reads the journal log superblock with `ujfs_get_logsuper`, displays/edits it, writes back with `ujfs_put_logsuper` if changed.

Display/edit helpers:
- `display_cbblfsck(struct fsck_blk_map_hdr *)`: prints fields such as eyecatchers, return code, block sizes, bad-block counts, relocation counts, LVM list count, and saved pointer fields. Allows field-by-field modification.
- `display_fsck_wsphdr(struct fsck_blk_map_hdr *)`: prints workspace header positions, timestamps, return code, fsck log offsets/status, and log write errors. Allows edits.
- `display_logsuper(struct logsuper *)`: prints log magic/version/serial, size, aggregate block size, flags, state name, end, UUID, label, and active filesystem UUIDs. Allows edits to main fields and parses UUID strings.

Workspace I/O:
- `get_fsckwsphdr(...)`: reads one page from global `fsckwsp_offset` using `xRead`, then endian-swaps with `ujfs_swap_fsck_blk_map_hdr`.
- `put_fsckwsphdr(...)`: swaps to disk order, writes one page with `xWrite`, then swaps back for continued in-memory use.

Integration points:
- Uses offsets initialized in `xpeek.c` from the mounted aggregate superblock.
- Uses `fsckcbbl.h`, `fsckwsp.h`, `jfs_logmgr.h`, `jfs_superblock.h`, `super.h`, and endian helpers.
- Shared UI parsing uses `m_parse`.

Notable behavior and risks:
- Several fields displayed/edited are pointer-valued fields from fsck structures; persisted pointer values are only meaningful in their original context and are risky to edit.
- Uses `%p` with manually prefixed `0x` in some output, which may print doubled prefixes on some C libraries.
- `jlog_super_offset` is declared extern but not used directly in this file.
- UUID edits validate format through `uuid_parse`; most other edits do not validate consistency.
