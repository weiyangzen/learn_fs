# sources/storage-engines/sqlite/ext/fts5/fts5_hash.c

## Purpose
`fts5_hash.c` implements the in-memory term hash used by FTS5 index writes to accumulate `term -> doclist` content before flushing it to a level-0 segment. It stores postings compactly in per-term allocations and supports exact term lookup and sorted prefix/full scans for flush and query integration.

## Important APIs and functions
- `sqlite3Fts5HashNew()` allocates a hash with 1024 slots, stores a pointer to the caller's byte counter, and copies the table detail mode.
- `sqlite3Fts5HashFree()` and `sqlite3Fts5HashClear()` release all entries while preserving/freeing the hash object as appropriate.
- `sqlite3Fts5HashWrite()` appends one token occurrence or delete marker for a rowid/column/position/key byte plus token.
- `fts5HashAddPoslistSize()` finalizes the previous row's poslist-size or detail-none marker bytes.
- `fts5HashResize()` doubles slot count when load reaches 50 percent.
- `sqlite3Fts5HashQuery()` returns a malloced copy of a single term doclist, including a finalized copy of pending poslist-size bytes.
- `sqlite3Fts5HashScanInit()`, `sqlite3Fts5HashScanNext()`, `sqlite3Fts5HashScanEof()`, and `sqlite3Fts5HashScanEntry()` sort matching entries and iterate term/doclist pairs.
- `fts5HashEntrySort()` and `fts5HashEntryMerge()` implement a nonrecursive merge-bucket sort over existing hash entries.

## Control flow
Each `Fts5HashEntry` allocation contains the struct, key bytes, a NUL terminator for scan convenience, and doclist bytes. The key is a one-byte index discriminator (`bByte`) followed by token bytes, so main and prefix indexes occupy the same hash namespace without colliding. On first write, the entry stores the absolute rowid varint and reserves a byte for the current row's poslist-size field. Later writes for the same row append column markers and position deltas depending on detail mode. Writes for a new row finalize the previous row's poslist metadata, append a rowid delta, and reserve the next poslist-size field.

For `detail=full`, positions are encoded as column-change markers plus offset deltas. For `detail=columns`, the code treats the column as the position-like value and writes at most one value per new column. For `detail=none`, content and delete flags are represented without full position data. Delete writes set `bDel`; content writes in detail-none set `bContent`.

Exact query looks up the key by hash slot and copies only the doclist payload into a caller-owned buffer, using a faux entry inside that buffer so `fts5HashAddPoslistSize()` can finalize the copy without mutating the original entry. Scans sort pointers to existing entries by key, finalize entries in place when exposed, and return pointers into the entry allocation.

## State and persistence behavior
State is transient and memory-resident until index sync flushes it. The byte counter pointed to by `pnByte` is updated by net entry-data growth in `sqlite3Fts5HashWrite()`, allowing the index layer to decide when the hash is large enough to flush. The hash itself does not write to SQLite storage; it supplies serialized doclists to the index layer. `sqlite3Fts5HashClear()` resets all slots and entry count after flush or rollback.

## Dependencies and integration points
The file depends on `Fts5Config.eDetail`, SQLite allocation APIs, varint helpers, big-endian 32-bit helpers, and internal FTS5 constants. It integrates with `fts5_index.c` write paths, prefix-index handling via `bByte`, query paths that need unflushed terms, and flush paths that scan entries in sorted key order before constructing segment pages.

## Risks and edge cases
- The doclist format is intentionally similar but not identical to on-disk doclists. Flush/query code must account for hash-specific trailing poslist-size handling.
- `sqlite3Fts5HashWrite()` assumes rowids and columns arrive in valid order; debug assertions check monotonic columns, but release builds rely on callers.
- Reallocation updates the slot chain pointer manually. Bugs here can corrupt the hash chain or leave stale pointers.
- `fts5HashEntrySort()` uses a fixed 32-entry merge-slot array. It relies on the hash load/entry count staying within ranges where repeated merging does not overrun `ap`.
- Scan APIs expose pointers into hash entries and may finalize entries in place, so callers must not mutate/clear the hash during scan.
- Detail-none delete/content marker handling is compact and easy to misinterpret; tests need both delete-only and content-bearing rows.

## Test signals
Tests should cover first insert, repeated same-row positions, rowid deltas, column transitions, prefix-index discriminator bytes, hash resize, exact query before and after poslist finalization, sorted scan order, prefix scan filtering, detail=full/columns/none encodings, delete markers, byte-counter updates, clear/free behavior, collision-heavy terms, and interleaving unflushed hash results with persisted index reads.
