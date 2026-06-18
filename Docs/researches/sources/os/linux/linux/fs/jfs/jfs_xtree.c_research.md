# File Research: sources/os/linux/linux/fs/jfs/jfs_xtree.c

JFS extent allocation descriptor B+tree manager for file data, symlink data, metadata files, and truncate-time block release.

Key responsibilities:
- Implements xtree page access and validation in `xt_getpage()`, rejecting corrupt `nextindex`/`maxentry` combinations.
- Maps logical block ranges to physical extents with `xtLookup()`, including sparse-hole misses and EOF checks.
- Searches xtrees with `xtSearch()`, maintaining traversal stacks, insertion split counts, next-extent hints, and sequential-access heuristics.
- Inserts extents with `xtInsert()`, allocating data blocks when needed, charging quotas, and rolling back allocation on failure.
- Splits full leaf, internal, and root pages through `xtSplitUp()`, `xtSplitPage()`, and `xtSplitRoot()`, including sibling links and router entries.
- Extends an existing adjacent extent in `xtExtend()`, creating a new extent when `MAXXLEN` would be exceeded.
- Updates not-recorded extents in `xtUpdate()`, supporting replacement, left/right coalescing, and two- or three-way extent splitting.
- Provides append-mode growth through `xtAppend()`, used by special sequential files such as the block map during online resize.
- Initializes inline inode roots with `xtInitRoot()`.
- Truncates extents and xtree index pages through `xtTruncate()` and `xtTruncate_pmap()`, with separate persistent-map and working-map behavior.
- Exposes optional statistics via `jfs_xtstat_proc_show()`.

Important interactions:
- Uses JFS metapage helpers through B-tree macros for root-inline and disk-page access.
- Uses block allocator functions such as `dbAlloc()`, `dbAllocBottomUp()`, `dbFree()`, `txFreeMap()`, and maplock structures.
- Uses quota accounting through `dquot_alloc_block()` and `dquot_free_block()`.
- Uses transaction logging through `txLock()`, `tlock`, `xtlock`, `tlckXTREE`, `tlckGROW`, `tlckNEW`, `tlckTRUNCATE`, `tlckFREE`, and relink locks.
- Updates inode state through `JFS_IP(ip)->i_xtroot`, `mode2`, `INLINEEA`, commit flags, and `ip->i_size`.
- Invalidates directory metadata pages when truncating directory xtrees.

Invariants and risks:
- Xtree pages must keep entries ordered by logical offset, with child-router entries pointing to ranges beginning at their keys.
- Root page block number is logically `0`; non-root pages are represented by `pxd_t` self descriptors.
- Insertions must avoid overlap with the next extent; otherwise `xtInsert()` returns `-EEXIST`.
- Split paths must release every pinned metapage exactly once; many error paths are sensitive to page ownership transfer.
- Quota and block-allocation rollback must stay paired, especially around split-page allocation and failed extent insertion.
- Truncate intentionally limits one transaction to `MAX_TRUNCATE_LEAVES` leaf pages to avoid transaction-lock exhaustion; callers may need iterative truncation.
- `COMMIT_Nolink` suppresses xtree logging for files with no directory links, so callers must choose the correct commit mode.
- Root expansion can consume inline EA space, and root shrink can restore `INLINEEA`; incorrect transitions can confuse fsck.
