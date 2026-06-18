# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_xtree.c

## Purpose

Implements the JFS extent allocation descriptor B+tree, called the xtree. It maps logical file block ranges to physical extents, mutates those mappings for file growth, recorded writes, appends, and truncation, and integrates those changes with JFS transaction logging, quotas, metapages, and allocation maps.

## Main Structures And Helpers

- `struct xtsplit` carries an insertion/split candidate while propagating page splits up the tree.
- `XT_CMP()` compares a logical block offset against an extent entry.
- `XT_PUTENTRY()` writes XAD flag, offset, length, and address fields.
- `xt_getpage()` wraps the JFS btree page fetch and performs structural sanity checks on `nextindex`, `maxentry`, and root/page capacity before returning an xtree page.

## Key Operations

- `xtLookup()` resolves a logical block range to a physical block range, returning holes with `*paddr = 0` and limiting `*plen` to the next extent or requested length.
- `xtSearch()` walks from the inline root down to a leaf, builds a `btstack`, and pins the found leaf. It has a sequential access fast path using `JFS_IP(ip)->btorder` and `btindex`, then falls back to binary search per xtree page.
- `xtInsert()` inserts a new extent, optionally allocating data blocks and charging quota. It rejects overlaps via `cmp` and `next`, marks new entries `XAD_NEW`, and either shifts a non-full leaf or delegates to `xtSplitUp()`.
- `xtSplitUp()`, `xtSplitPage()`, and `xtSplitRoot()` split full leaves/internal pages, allocate new index pages, update sibling pointers, create router entries, and propagate split keys upward. Root splits copy the inline root into a real child page and convert the inline root to an internal page.
- `xtExtend()` extends the previous extent in place when contiguous and splits into an additional XAD if the length exceeds `MAXXLEN`.
- `xtUpdate()` converts an allocated-but-not-recorded extent into a recorded one. It handles replacement, left/right coalescing, and two- or three-way splitting of an existing XAD.
- `xtAppend()` is optimized for append-mode growth, including bottom-up allocation for data and potential xtree index pages.
- `xtInitRoot()` initializes an inline xtree root in the inode, using fewer initial slots for non-directories to leave room for inline EA.
- `xtTruncate()` truncates xtree/data extents and index pages from the right side of the tree, with separate behavior for persistent/working map update modes. It limits a single transaction to `MAX_TRUNCATE_LEAVES` to avoid exhausting metapages and tlocks.
- `xtTruncate_pmap()` logs persistent-map freeing for zero-link files while leaving the working map and xtree available for open file handles.
- `jfs_xtstat_proc_show()` exposes search/split counters when `CONFIG_JFS_STATISTICS` is enabled.

## Locking, Transactions, And Lifetime

Metapages returned by xtree search/split paths are pinned until explicitly released with `XT_PUTPAGE()`. Mutations mark metapages dirty and generally acquire `txLock()` records unless the inode is marked `COMMIT_Nolink`. Quota charging happens before block allocation for new data/index extents and is rolled back on allocation/split failures where possible. Truncation uses transaction lock types such as `tlckTRUNCATE`, `tlckFREE`, and map locks to defer or perform block freeing according to commit mode.

## Error Handling And Integrity Notes

The file treats corrupt tree shape as filesystem corruption via `jfs_error()` and returns `-EIO`. Stack overflow in tree descent is guarded with `BT_STACK_FULL()`. Split paths have several pinned-page transfer points; correct `XT_PUTPAGE()` pairing is central to safety. The `xtSplitUp()` return path maps some split failures to `-EIO`, so callers lose the original error in one branch. Truncation intentionally may return a nonzero new size to signal the caller to continue in another transaction.
