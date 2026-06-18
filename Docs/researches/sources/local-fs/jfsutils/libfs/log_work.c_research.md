# File Research: sources/local-fs/jfsutils/libfs/log_work.c

This is the main journal replay work engine. `jfs_logredo()` in `logredo.c` reads records backward; this file decides which committed records matter, applies after-images to pages, rebuilds allocation-state working maps, and installs no-redo filters so older log records cannot overwrite newer recovered state.

Major data structures:
- Commit table: `com[]`, `comhash[]`, `comfree`, tracking committed transaction IDs while replay scans backward.
- Redo page table: `struct doblk`, `blkhash[]`, tracking which portions of each page/extent have already been updated in this replay pass.
- NoRedoFile table: `struct nodofile`, `nodofilehash[]`, suppressing later processing for deleted inodes.
- Extended dtpage list: `struct ExtDtPg`, used to defer freelist rebuilds for directory pages extended during replay.

Main functions:
- `doCommit()` inserts a transaction ID; `findCommit()` tests it; `deleteCommit()` removes it when the transaction start is reached and sets `end_of_transaction`.
- `doAfter()` handles committed `LOG_REDOPAGE` records, skips clean/error volumes and deleted files, calls `updatePage()`, and marks newly allocated dtree/xtree pages in the block map.
- `doNoRedoFile()` installs inode-level no-redo filters.
- `doNoRedoPage()` installs page/tree-root no-redo filters and frees non-root dtree pages in the block map.
- `doNoRedoInoExt()` installs four page filters for a released inode extent, updates the bmap, and clears IAG extent metadata if no newer inode activity was seen.
- `doUpdateMap()` applies committed bmap-only records for PXD/XAD allocation and free operations.
- `dtpg_resetFreeList()` and `dtrt_resetFreeList()` reconstruct directory page/root freelists from slot tables and entry continuation chains.
- `findPageRedo()` looks up or allocates `doblk` records.
- `logredoInit()` initializes commit/hash state, buffer LRU state, no-redo storage, and opens affected volumes.
- `markBmap()` and `markImap()` update persistent maps only where the per-session working maps say the state is not yet determined.
- `saveExtDtPg()` records extended dtree pages for late freelist rebuilding.
- `updatePage()` is the central page after-image applier for inode, btroot xtree/dtree, non-root xtree, non-root dtree, and data records.

Control-flow model:
- Replay is LIFO. The newest log records are processed first, so per-page `doblk` summaries and map `wmap` bits prevent older records from overwriting the final state.
- Redopage data is parsed right-to-left as `<segmentData><offset,length>` segments.
- Inode records update base images, inline data, inline EA, symlink data, inode allocation maps, no-redo filters for zero-link inodes, and bmap state for allocated inode extents.
- Xtree records use low-water marks plus header flags to apply only the newest xad range; `MARKXADNEW` marks newly allocated/extended extents in the bmap and clears transient xad flags.
- Dtree records track 32-byte slots using bit vectors, with special handling for variable-sized non-root dtree pages.
- Directory freelists for extended dtpages are postponed until all older records affecting the previous shorter page form have been processed.

Integration points:
- Uses global `vopen[]`, `bufhdr[]`, `afterdata[]`, `logsup`, and memory fallback state from `logredo.c`.
- Uses `bread()`, `openVol()`, `alloc_storage()`, `dMapGet()`, `iagGet()`, `fsError()`, and `fsck_send_msg()`.
- Depends heavily on JFS on-disk layout headers: dinodes, dtree, xtree, dmap, imap, and log manager structures.

Risks and invariants:
- The correctness invariant is “newest replay decision wins”; `wmap`, `doblk`, NoRedoFile, and NoRedoPage must stay consistent.
- `deleteCommit()` assumes the transaction exists in the hash chain; callers only invoke it after `findCommit()`, which preserves that invariant.
- Allocation fallback can cannibalize bmap workspace; if that happens, logredo may still finish data replay but reports `ENOMEM25` so fsck rebuilds maps.
- Several data format errors intentionally force full fsck or log reformat by returning negative codes.
