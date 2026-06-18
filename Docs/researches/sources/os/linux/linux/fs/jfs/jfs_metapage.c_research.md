# File Research: sources/os/linux/linux/fs/jfs/jfs_metapage.c

Implements JFS metadata-page management on top of Linux folios. A metapage represents a filesystem metadata block or 4K metadata page, carries transaction/logsync state, and supplies custom address-space operations for metadata inodes.

Core responsibilities:
- Allocate/free `struct metapage` objects from a slab-backed mempool.
- Attach one or more metapages to a folio. When `PAGE_SIZE > PSIZE`, a `meta_anchor` tracks multiple metapages and outstanding I/O count/status for the folio.
- Provide locking around each metapage while temporarily dropping and reacquiring the folio lock to avoid deadlock.
- Resolve metadata file logical blocks to physical blocks through `xtLookup()` in `metapage_get_blocks()`.
- Read metadata folios with bios and complete them through `metapage_read_end_io()`.
- Write dirty metapages with contiguous-bio coalescing in `metapage_write_folio()`.
- Remove written metapages from the log sync list after home write completion.
- Release, invalidate, and migrate folios containing metapage private state.

Key exported operations:
- `metapage_init()` / `metapage_exit()` create and destroy the slab/mempool.
- `__get_metapage()` maps or reads the target folio, finds/creates a metapage at the requested offset, validates logical size, locks it, and optionally zeroes it for new metadata.
- `grab_metapage()` adds a reference and locks an existing metapage.
- `release_metapage()` unlocks, decrements references, marks dirty/sync, writes synchronously if needed, removes logsync state if clean, and drops unused metapages.
- `force_metapage()` forces synchronous writeback of a metadata page.
- `hold_metapage()` / `put_metapage()` support callers that need to hold the folio lock across metapage homeok transitions.
- `__invalidate_metapages()` marks direct-inode metapages in an extent as discarded and removes any logsync state.

Address-space integration:
- `jfs_metapage_aops` provides `read_folio`, `writepages`, `release_folio`, `invalidate_folio`, `dirty_folio`, and optional `migrate_folio`.
- Writeback skips `nohomeok` metapages unless forcewrite is set, redirties them, and may flush the journal to unblock them.

Important invariants:
- Dirty metadata protected by a transaction is marked `nohomeok`; writeback must not send it home until the journal commit is durable.
- `mp->lsn` membership in a log sync list must be cleared only under the corresponding log sync lock.
- Folio private data may be either a single metapage or a `meta_anchor` depending on `MPS_PER_PAGE`.
