# Research: sources/storage-engines/sqlite/ext/fts5/fts5_index.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008737`: lines 1-8345, `Docs/researches/chunks/subset-b-008737_research.md`
- `subset-b-008738`: lines 8346-9560, `Docs/researches/chunks/subset-b-008738_research.md`

## Chunk Research

### subset-b-008737: lines 1-8345

# sources/storage-engines/sqlite/ext/fts5/fts5_index.c lines 1-8345

## Scope And Purpose

This chunk contains most of SQLite FTS5's low-level index storage engine. It implements read, write, query, merge, delete, contentless-delete, secure-delete, prefix-query, tokendata, and the beginning of integrity-check support for the `%_data` and `%_idx` backing tables owned by an FTS5 virtual table.

The top-level contract is described in the opening comments: `%_data(id INTEGER PRIMARY KEY, block BLOB)` stores structure records, averages, segment leaf pages, doclist-index pages, and contentless-delete tombstone hash pages. `%_idx(segid, term, pgno, PRIMARY KEY(segid, term))` stores term-to-segment-page routing entries used to seek directly into segment b-trees. Other FTS5 code calls this module through APIs declared in `fts5Int.h`; this file owns the binary formats and most of the state transitions that make the FTS index durable and queryable.

The requested chunk ends inside the debug/integrity-check section, after `fts5TestTerm()` has begun but before the rest of integrity-check and debug decoding helpers. The final per-file research should merge this with later chunks for the rest of `fts5_index.c`.

## Storage Format

The file defines fixed rowids for singleton records:

- `FTS5_AVERAGES_ROWID` stores the row count and total token counts per column.
- `FTS5_STRUCTURE_ROWID` stores the segment hierarchy and merge state.

Segment leaves, doclist-index pages, and tombstone pages use rowids composed from segment id, doclist-index flag, tree height, and page number. The important macros are `FTS5_SEGMENT_ROWID()`, `FTS5_DLIDX_ROWID()`, and `FTS5_TOMBSTONE_ROWID()`. The tombstone rowid macro offsets segment ids by `1<<16` so contentless-delete hash pages live outside normal segment/data rowid ranges.

The structure record has a legacy format and a V2 format identified by `FTS5_STRUCTURE_V2`. V2 is used by `contentless_delete=1` tables and extends each segment with origin range, number of tombstone pages, counted tombstone entries, and segment entry count. `fts5StructureDecode()` and `fts5StructureWrite()` are the authoritative serializer/deserializer pair.

Segment leaf pages begin with a 4-byte header: first-rowid offset and leaf-body size. The leaf body contains prefix-compressed terms, delta-encoded doclists, and position lists. The footer is a page index of term offsets. Doclists may span leaf pages; when they do, termless pages and first-rowid header offsets allow forward and reverse iteration without loading entire doclists. Large spanning doclists may also have doclist-index b-trees that copy first rowids for termless pages and support seeks within a doclist.

Contentless-delete tombstones are stored as per-segment open-addressed hash pages. The page header records key size, rowid-zero flag, and entry count. Slots are either 4-byte or 8-byte big-endian rowids. Query and rebuild paths are `fts5IndexTombstoneQuery()`, `fts5IndexTombstoneAddToPage()`, `fts5IndexTombstoneRehash()`, and `fts5IndexTombstoneRebuild()`.

## Important Types

`Fts5Index` is the module handle. It stores the virtual-table config, `%_data` table name, in-memory `Fts5Hash`, pending write counters, error state, prepared statements, read-only blob handle, cached structure pointer, and data-version used to identify cached structure freshness.

`Fts5Structure`, `Fts5StructureLevel`, and `Fts5StructureSegment` model the persistent segment tree. Levels contain oldest-to-newest segment arrays and `nMerge` tracks incremental merge inputs. Segments carry leaf page ranges, segment ids, and V2 contentless-delete metadata.

`Fts5Data` wraps a raw `%_data` blob plus its total size and leaf-body size. Reads pad allocation with zero bytes so varint and corruption handling can avoid unsafe overreads.

`Fts5SegIter` iterates through a single segment or in-memory hash doclist. It tracks current leaf page, term, rowid, position-list offset/size, doclist-index iterator, reverse-iteration offsets, and lazily loaded tombstone pages.

`Fts5Iter` is the merged iterator returned to higher layers. It contains a power-of-two array of `Fts5SegIter` objects and a tournament tree (`aFirst`) that selects the next term/rowid across all segments. It also owns output buffers and optional `Fts5Colset` filtering.

`Fts5SegWriter`, `Fts5PageWriter`, and `Fts5DlidxWriter` write segment leaves, page footers, `%_idx` entries, and doclist-index b-trees.

`Fts5TokenDataIter` and `Fts5TokenDataMap` support `tokendata=1` and `xInstToken()` by mapping rowid/position pairs back to the token term that produced them.

`Fts5TombstoneArray` is a reference-counted, lazily populated array of tombstone hash pages shared across related segment iterators.

## Data Access And Structure Management

`fts5DataRead()` is the central `%_data` reader. It reuses a read-only incremental blob handle when possible, reopens it for the requested rowid, treats `SQLITE_ERROR` from blob open/reopen as virtual-table corruption, allocates padded `Fts5Data`, reads the blob, sets `szLeaf`, increments `nRead`, and stores failures in `Fts5Index.rc`. `fts5LeafRead()` adds leaf-specific validation that `szLeaf` is within bounds.

`fts5DataWrite()` uses a cached `REPLACE INTO %_data(id, block)` statement. `fts5DataDelete()` deletes rowid ranges. `fts5DataRemoveSegment()` deletes all normal leaf/doclist-index records for a segment, deletes tombstone pages if present, and removes `%_idx` rows for the segment.

`fts5IndexPrepareStmt()` centralizes persistent prepared-statement creation and treats missing or altered backing tables as corruption when prepare returns `SQLITE_ERROR`.

`fts5StructureRead()` caches the decoded structure object, keyed by `PRAGMA data_version`, and `fts5StructureInvalidate()` drops the cache after writes or rollback. Structure objects are reference-counted because iterators and mutation paths may share them; `fts5StructureMakeWritable()` clones when a shared structure must be edited.

Structure promotion and merge planning are handled by `fts5StructurePromoteTo()`, `fts5StructurePromote()`, `fts5IndexMerge()`, `fts5IndexAutomerge()`, and `fts5IndexCrisismerge()`. Promotion keeps very small or newly large segments from remaining on poorly chosen levels, while automerge and crisismerge bound the number of segments accumulated by writes.

## Segment And Multi-Iterator Control Flow

Single-segment iteration starts with `fts5SegIterInit()` for full scans, `fts5SegIterSeekInit()` for exact/GE seeks, `fts5SegIterNextInit()` for tokendata continuation, or `fts5SegIterHashInit()` for in-memory hash contents. The iterator chooses its `xNext` function based on reverse mode and `detail=none`.

Forward iteration is split between `fts5SegIterNext()` and `fts5SegIterNext_None()`. They advance within a doclist, cross leaf-page boundaries, decode new terms, decode rowid deltas, and set position-list output state. `fts5SegIterLoadTerm()`, `fts5SegIterLoadRowid()`, and `fts5SegIterLoadNPos()` are the core decoders.

Reverse iteration uses `fts5SegIterReverse()`, `fts5SegIterReverseInitPage()`, and `fts5SegIterReverseNewPage()` to locate the last rowid in a doclist, build rowid-offset tables for the current page, and walk backward through pages. If a doclist-index exists, `fts5SegIterNextFrom()` can jump closer to a requested rowid before scanning.

Doclist-index iteration is implemented by `Fts5DlidxIter` and helpers from `fts5DlidxLvlNext()` through `fts5DlidxIterPgno()`. These functions traverse single or multi-level doclist-index b-trees in forward or reverse order and expose leaf page/first-rowid pairs to segment iterators.

`fts5MultiIterNew()` allocates and initializes a merged iterator over all structure segments and optionally the in-memory hash. `fts5MultiIterFinishSetup()` builds a tournament tree over sub-iterators. `fts5MultiIterNext()` advances the winner, skips duplicate lower-priority entries, applies delete-marker and tombstone filtering, and sets public output fields. `fts5MultiIterNext2()` is a lighter variant for prefix scans that need to know when a new term might have started.

The merge tree treats segment ordering as priority: newer segments shadow older entries with the same term/rowid. `fts5MultiIterIsEmpty()` detects delete markers with empty position lists, and `fts5MultiIterIsDeleted()` checks contentless-delete tombstones.

## Position Lists, Column Filters, Prefix Queries, And Tokendata

`fts5ChunkIterate()` streams a position list that may span leaf pages to a callback. `fts5SegiterPoslist()` uses it to either copy a full position list or filter it by a column set. Output callbacks handle `detail=full`, `detail=columns`, and `detail=none` differences.

`fts5IterSetOutputCb()` chooses one of several output callbacks: no output, detail-none row count behavior, direct no-colset output, zero-colset output, full-detail filtering, or optimized detail-column filtering for <=100 columns.

Prefix queries are not always satisfied by a dedicated prefix index. `sqlite3Fts5IndexQuery()` selects a prefix index when one has matching character length, can use the next-longer prefix index plus the main index for some cases, or falls back to scanning main-index terms. `fts5VisitEntries()` provides the generic term-range visitor used by prefix setup. `fts5SetupPrefixIter()` merges all matching term doclists into a synthetic doclist and wraps it with `fts5MultiIterNew2()`.

Prefix doclist merging uses `fts5MergeRowidLists()` for `detail=none` and `fts5MergePrefixLists()` for full/column detail. The latter merges duplicate rowids and sorted position lists, carefully preserving varint encoding and allocating padding for corrupt-input detection.

`tokendata=1` handling is more complex because multiple indexed terms may correspond to a single query token. `fts5SetupTokendataIter()` builds a set of iterators, one for each indexed term matching the token-data prefix form. `fts5IterSetOutputsTokendata()` merges row outputs across those iterators and, for full detail, accumulates maps from row positions to term iterators. `sqlite3Fts5IterToken()`, `sqlite3Fts5IndexIterClearTokendata()`, and `sqlite3Fts5IndexIterWriteTokendata()` expose or populate the token maps used by `xInstToken()`.

## Write, Flush, Merge, And Delete Behavior

Writes enter through `sqlite3Fts5IndexBeginWrite()` and `sqlite3Fts5IndexWrite()`. `BeginWrite` ensures the in-memory hash exists and flushes it if rowid order changes, a delete follows an insert for the same rowid, or the hash exceeds `nHashSize`. `IndexWrite` writes the token to the main index and to configured prefix indexes using index prefix bytes starting at `FTS5_MAIN_PREFIX`.

`fts5IndexFlush()` flushes pending hash data or pending contentless deletes by calling `fts5FlushOneHash()`. The flush path scans hash terms in order, writes a new level-0 segment through `Fts5SegWriter`, updates structure metadata, promotes segments as needed, runs automerge and crisismerge, writes the structure record, and clears the hash on success.

Segment writing is assembled from `fts5WriteInit()`, `fts5WriteAppendTerm()`, `fts5WriteAppendRowid()`, `fts5WriteAppendPoslistData()`, `fts5WriteFlushLeaf()`, `fts5WriteFlushBtree()`, and `fts5WriteFinish()`. These functions maintain leaf headers, page-index footers, prefix-compressed terms, delta rowids, position-list splitting at varint boundaries, doclist-index pages, and `%_idx` split keys.

Incremental merge is handled by `fts5IndexMergeLevel()`. It opens a multi-iterator across input segments, writes a merged output segment, drops annihilated delete markers when allowed, preserves delete markers when necessary, trims partially consumed input segments if the work budget runs out, and deletes fully consumed segments from `%_data` and `%_idx`. `fts5TrimSegments()` rewrites the first remaining page of partially merged inputs so future merge steps resume correctly.

Ordinary delete operations are represented as delete markers in doclists and resolved during merge. Secure-delete mode is different: `fts5FlushSecureDelete()` upgrades the table version to `FTS5_CURRENT_VERSION_SECUREDELETE` if needed, seeks the existing term/rowid, and calls `fts5DoSecureDelete()` to rewrite existing segment leaf pages so the term occurrence is physically removed. `fts5SecureDeleteOverflow()` removes overflow position-list bytes from following pages, and `fts5SecureDeleteIdxEntry()` removes `%_idx` entries when secure deletion removes the last term from a leaf.

Contentless-delete mode uses V2 structure records and tombstone hash pages instead of editing segment contents immediately. `sqlite3Fts5IndexContentlessDelete()` finds segments whose origin range covers the deleted origin, increments counted tombstones once, and calls `fts5IndexTombstoneAdd()` for each matching segment. Tombstone additions may rewrite one hash page or rebuild the hash with more pages or a larger key size. Later reads skip tombstoned rowids, and `fts5IndexFindDeleteMerge()` can choose levels for delete-driven merge work when tombstone density exceeds the `deletemerge` threshold.

## Public APIs In This Chunk

Key external functions implemented in this span include:

- `sqlite3Fts5IndexOpen()`, `sqlite3Fts5IndexClose()`, and `sqlite3Fts5IndexReinit()` for lifecycle and backing table initialization.
- `sqlite3Fts5IndexBeginWrite()`, `sqlite3Fts5IndexWrite()`, `sqlite3Fts5IndexSync()`, and `sqlite3Fts5IndexRollback()` for write transactions.
- `sqlite3Fts5IndexQuery()`, `sqlite3Fts5IterNext()`, `sqlite3Fts5IterNextScan()`, `sqlite3Fts5IterNextFrom()`, `sqlite3Fts5IterTerm()`, `sqlite3Fts5IterToken()`, `sqlite3Fts5IterClose()`, and tokendata helpers for query iteration.
- `sqlite3Fts5IndexOptimize()` and `sqlite3Fts5IndexMerge()` for explicit maintenance commands.
- `sqlite3Fts5IndexGetAverages()` and `sqlite3Fts5IndexSetAverages()` for the averages record.
- `sqlite3Fts5IndexSetCookie()`, `sqlite3Fts5IndexLoadConfig()`, `sqlite3Fts5IndexGetOrigin()`, `sqlite3Fts5IndexReads()`, and `sqlite3Fts5IndexContentlessDelete()` for metadata, diagnostics, and special table modes.
- `sqlite3Fts5IndexEntryCksum()` and the beginning of debug-only integrity helpers.

## Dependencies And Integration Points

This file depends heavily on internal FTS5 services declared in `fts5Int.h`: configuration loading and error reporting, `Fts5Hash`, `Fts5Buffer`, varint helpers, position-list readers/writers, memory helpers, and query flags such as `FTS5INDEX_QUERY_PREFIX`, `FTS5INDEX_QUERY_DESC`, `FTS5INDEX_QUERY_SCAN`, and `FTS5INDEX_QUERY_SKIPEMPTY`.

It integrates with SQLite core through incremental blob I/O, prepared statements, `sqlite3_step/reset/finalize`, `sqlite3_mprintf`, `sqlite3_malloc64/realloc64/free`, `PRAGMA data_version`, and SQLite result codes. It also assumes the FTS5 virtual table layer has created `%_data`, `%_idx`, and `%_config` tables and that tokenizer/front-end code calls writes in acceptable rowid order.

The FTS query layer consumes `Fts5IndexIter` outputs (`iRowid`, `pData`, `nData`, `bEof`) and may call term/token helpers for vocab and `xInstToken()` behavior. The maintenance command layer calls optimize/merge APIs. Integrity-check code later in the file calls checksumming helpers and reissues index queries through this same public interface.

## State And Persistence Behavior

Persistent state is stored in `%_data`, `%_idx`, and `%_config`. `%_data` contains all binary blobs for structure, averages, segment leaves, doclist-index pages, and tombstone hash pages. `%_idx` is a routing index for term seeks. `%_config` is touched by secure-delete upgrade logic to persist the index version.

In-memory state is buffered in `Fts5Hash` until flush, with `nPendingData`, `nPendingRow`, `iWriteRowid`, and `bDelete` enforcing write ordering and flush thresholds. `flushRc` preserves flush errors while pending data remains. `nContentlessDelete` makes deletes contribute extra automerge work and is cleared on flush or discard.

The structure cache is explicitly invalidated around writes, rollback, reinit, and flush paths. Reference counting allows safe handoff to callers that need stable structure snapshots. Prepared statements and blob handles are cached for speed and closed/finalized at handle close or reader close.

Segment merge and secure-delete operations mutate existing persistent blobs in place, so corruption checks guard offsets, page bounds, rowid ordering, and footer consistency. Ordinary insert/delete writes append new segment data; automerge later rewrites merged segments and deletes obsolete ranges.

## Risks And Edge Cases

This code is high risk because it is both the FTS5 binary-format implementation and the query engine over that format.

- Corrupt or adversarial `%_data` blobs can produce invalid offsets, malformed varints, impossible page ranges, or overlapping segments. The code contains many `FTS5_CORRUPT_*` checks, but every decoder change needs careful bounds reasoning.
- `detail=none`, `detail=columns`, and `detail=full` use different position-list encodings and iteration paths. Fixes in one path may not apply to the others.
- Reverse iteration and `NextFrom()` depend on doclist-index metadata and per-page offset reconstruction. Off-by-one errors can silently skip or duplicate rowids.
- The tournament merge tree must preserve priority order across in-memory hash data and on-disk segments so newer delete markers or replacements shadow older entries.
- Prefix query fallback materializes a synthetic doclist. Large prefix ranges can be memory-intensive, and the merge code has special corruption padding to avoid overflow on malformed inputs.
- Secure-delete rewrites leaf bodies and footers in place, including overflow pages and `%_idx` entries. This path is especially sensitive to term/footer offset consistency.
- Contentless-delete tombstone hashes are rebuilt dynamically and use modulo page selection plus open addressing. Key-size upgrades, rowid zero, full pages, and counted tombstone metadata must stay synchronized with structure records.
- Structure V2 compatibility matters: legacy databases must remain readable, while contentless-delete tables require origin counters and tombstone metadata to persist accurately.
- Blob readers can be invalidated by savepoint rollback; `fts5DataRead()` handles `SQLITE_ABORT` by reopening, but transaction-bound state changes remain subtle.
- Segment id allocation assumes `FTS5_MAX_SEGMENT` and checks `%_idx` in debug builds only. Production correctness depends on structure records accurately listing all live segments.

## Test Signals

Useful validation signals for this chunk include:

- FTS5 insert/query/delete tests across `detail=full`, `detail=columns`, and `detail=none`, including prefix indexes and no-prefix-index fallback scans.
- Rowid ascending and descending query tests, especially `sqlite3Fts5IterNextFrom()` with large doclists that require doclist-index jumps.
- Prefix query tests with multiple matching terms, duplicate rowids, merged position lists, column filters, and `tokendata=1`/`xInstToken()` behavior.
- Maintenance tests for automerge, crisismerge, explicit `merge`, and `optimize`, verifying segment counts, `%_idx` entries, and query results before and after merges.
- Secure-delete tests that inspect database bytes or use debug helpers to confirm deleted tokens and `%_idx` entries are physically removed.
- Contentless-delete tests covering origin ranges, tombstone hash growth/rebuild, rowid zero, 4-byte to 8-byte key upgrades, deletemerge selection, and query filtering of tombstoned rows.
- Corruption tests that mutate structure records, leaf headers, page footers, doclist-index pages, and tombstone pages and expect `SQLITE_CORRUPT_VTAB` plus useful FTS5 error messages.
- Transaction tests for rollback/savepoint behavior, reader invalidation, flush error persistence, and structure cache invalidation.
- Integrity-check/debug builds that exercise `fts5TestDlidxReverse()`, query checksum comparisons, prefix-index cross-checking, and UTF-8 term validation. The remainder of the integrity-check implementation appears after this chunk and should be covered by the adjacent research document.

### subset-b-008738: lines 8346-9560

# sources/storage-engines/sqlite/ext/fts5/fts5_index.c lines 8346-9560

## Scope

This chunk covers the end of the FTS5 index integrity-check implementation and the test/debug helpers registered by `sqlite3Fts5IndexInit()`. It starts inside the debug-only `fts5TestTerm()` query cross-check, then covers segment/page-index integrity validation, full index checksum validation, `fts5_decode()` and `fts5_decode_none()` record decoders, `fts5_rowid()`, the `fts5_structure` table-valued function, and `sqlite3Fts5IndexReset()`.

The code is split between production integrity checking and diagnostics compiled only with `SQLITE_TEST` or `SQLITE_FTS5_DEBUG`. Normal builds still include the integrity-check entry point and reset logic, while the scalar/table-valued debugging aids are registered as no-ops outside those debug/test feature gates.

## Purpose

- Validate that FTS5 on-disk segment metadata, `%_idx` entries, leaf page contents, doclist-index records, and index checksums agree with each other.
- Compare the checksum of actual index contents with the checksum expected by the storage layer during FTS5 integrity checks.
- In `SQLITE_DEBUG` builds, run additional expensive self-checks that compare forward and reverse query results, prefix-index results against no-index scans, and doclist-index forward/reverse iteration.
- Provide human-readable decoding of FTS5 `%_data` records for tests and debugging through `fts5_decode()` and `fts5_decode_none()`.
- Provide `fts5_rowid('segment', segid, pgno)` so tests can compute segment-data rowids without duplicating internal rowid packing rules.
- Expose serialized FTS5 structure records through the debug-only `fts5_structure` virtual table, including segment id, level, merge state, leaf range, contentless-delete origins, and tombstone counts.
- Invalidate the cached `Fts5Structure` if `PRAGMA data_version` changed since it was read.

## Important APIs, Types, And Functions

- `fts5TestTerm()` is debug-only. For each term transition during a linear integrity scan, it queries the previous term and verifies ASC/DESC checksum parity. For prefix indexes it can also compare indexed prefix results against `FTS5INDEX_QUERY_TEST_NOIDX` scans when pending hash data is empty and the term bytes are valid UTF-8.
- `fts5IndexIntegrityCheckEmpty()` verifies that leaf pages in a gap exist, have no terms, and optionally have no first-rowid pointer. It is used to validate empty pages between `%_idx` split-key entries and doclist-index-covered ranges.
- `fts5IntegrityCheckPgidx()` reconstructs each term referenced by a leaf page-index (`pgidx`), checks that offsets stay inside the leaf body, verifies prefix-compressed term reconstruction bounds, and enforces strictly increasing term order.
- `fts5IndexIntegrityCheckSegment()` validates a single `Fts5StructureSegment`. It scans `%_idx` rows for the segment, reads each referenced leaf, verifies split-key ordering, validates the leaf `pgidx`, checks empty leaves between indexed leaves, and validates doclist-index entries when present.
- `sqlite3Fts5IndexIntegrityCheck()` is the public index-layer integrity API used by FTS5 storage. It loads the current `Fts5Structure`, checks every segment, scans all terms and rowids with a multi-iterator, computes `sqlite3Fts5IndexEntryCksum()` values, and optionally compares the result with the caller-provided checksum.
- `fts5DecodeRowid()` unpacks `%_data` rowid bits into tombstone flag, segment id, doclist-index flag, tree height, and page number. `fts5DebugRowid()` formats those components.
- `fts5DecodeStructure()` and `fts5DebugStructure()` decode a serialized `Fts5Structure` blob and print levels, merge counts, segment ids, leaf ranges, and origin ranges.
- `fts5DecodeAverages()`, `fts5DecodePoslist()`, `fts5DecodeDoclist()`, and `fts5DecodeRowidList()` decode specific `%_data` payload formats into textual output.
- `fts5DecodeFunction()` implements both `fts5_decode()` and `fts5_decode_none()`. It pads a copy of the input blob, decodes by rowid kind, and dispatches to structure, averages, doclist-index, tombstone-hash, detail=none leaf, or normal/detail leaf decoding.
- `fts5RowidFunction()` implements `fts5_rowid()`, currently supporting only the `"segment"` subject.
- `Fts5StructVtab` and `Fts5StructVcsr` implement the `fts5_structure` virtual table cursor over a decoded structure blob supplied through the hidden `struct` column.
- `sqlite3Fts5IndexInit()` registers debug/test SQL helpers: `fts5_decode`, `fts5_decode_none`, `fts5_rowid`, and the `fts5_structure` module.
- `sqlite3Fts5IndexReset()` compares `fts5IndexDataVersion(p)` with `p->iStructVersion` and calls `fts5StructureInvalidate()` on mismatch.

## Control Flow

`sqlite3Fts5IndexIntegrityCheck()` first calls `fts5StructureRead()`. If no structure can be loaded, it returns the existing `Fts5Index.rc` through `fts5IndexReturn()`. Otherwise it walks every level and segment in the structure and calls `fts5IndexIntegrityCheckSegment()` for each one.

Segment integrity checking scans `%_idx` with `SELECT segid, term, (pgno>>1), (pgno&1) ... ORDER BY 1, 2`. For each usable split-key row, it reads the corresponding leaf from `%_data`. A non-empty leaf must have a first term greater than or equal to the split key, a rowid pointer before the first term, and a valid page-index. A secure-delete special case allows the very first segment page to remain represented in `%_idx` even if it has been reduced to an empty four-byte leaf. Gaps before each indexed leaf are checked as termless leaves. If the `%_idx` row advertises a doclist-index, the code iterates it, verifies rowid-less intermediate leaves, and confirms each advertised leaf contains the expected first rowid, with relaxed comparisons for secure-delete pages that may have had rowids removed.

After structural validation, `sqlite3Fts5IndexIntegrityCheck()` scans all index entries with `fts5MultiIterNew(... FTS5INDEX_QUERY_NOOUTPUT ...)`. For `detail=none`, non-empty entries contribute one checksum item per rowid. For other detail modes, the code materializes the current position list, appends zero padding, iterates positions with `sqlite3Fts5PoslistNext64()`, and adds one checksum item per column/token offset. If `bUseCksum` is true and the computed checksum differs from the storage-layer checksum, it reports an FTS5 corruption error for the table.

In debug builds, the linear scan also calls `fts5TestTerm()` whenever the term changes. That helper queries the previous term normally and in descending order, then for prefix indexes optionally queries with the prefix index disabled. The accumulated query checksum must match the linear-scan checksum at the same point. This gives coverage for query paths that a pure linear scan would not exercise.

The decode path starts in `fts5DecodeFunction()`. It copies the SQL blob argument into a newly allocated buffer with `FTS5_DATA_ZERO_PADDING` bytes of trailing zeros, decodes the rowid, appends a formatted rowid prefix, then selects a decoding strategy. Doclist-index rows are stepped with `fts5DlidxLvlNext()`. Tombstone hash pages print element counts and non-zero slots. Segment id zero rows decode as averages or structure records. Detail=none leaf pages decode rowid lists and prefix-compressed terms. Normal leaf pages decode any leading poslist/doclist tail, then use the page-index to find each term/doclist boundary.

The `fts5_structure` virtual table requires an equality constraint on hidden column `struct`. `xFilter` decodes that blob into an `Fts5Structure`, initializes the cursor before the first segment, and calls `xNext`. `xNext` advances segment then level, releasing the decoded structure at EOF. `xColumn` maps cursor state to level, segment ordinal, merge flag, segid, leaf range, origin range, tombstone page count, tombstone entry count, and segment entry count.

## State And Persistence Behavior

The integrity-check functions do not intentionally mutate index contents. They read `%_data`, `%_idx`, and the serialized structure record, and mutate only in-memory error/check state:

- `Fts5Index.rc` carries corruption, OOM, SQL, and finalize errors through helper calls.
- `sqlite3Fts5ConfigErrmsg()` records table-specific corruption messages for rowid/blob failures and checksum mismatches.
- Temporary `Fts5Buffer` instances hold reconstructed terms, position lists, decoded output, and previous-term state.
- `Fts5Data` pages read from `%_data` are reference-count-neutral local objects released after each check or decode.
- `Fts5DlidxIter` and `Fts5Iter` instances are transient iterators over doclist-index pages and merged segment contents.
- `Fts5StructVcsr.pStruct` owns a decoded structure while the debug virtual table cursor is active and releases it at EOF or close.

Persistent storage assumptions are central to the checks. `%_idx.pgno` packs a leaf page number and doclist-index flag; `%_data` segment rowids are built by `FTS5_SEGMENT_ROWID()` and unpacked by `fts5DecodeRowid()` in debug tools; leaf bodies store rowid offsets, page-index offsets, term data, doclists, and optional doclist-index references; secure-delete and contentless-delete modes allow tombstone metadata and removed entries that make some exact equality checks intentionally looser.

`sqlite3Fts5IndexReset()` is the only routine here that changes cached index state in normal operation. It reads the database data-version and invalidates `p->pStruct` if another connection or operation changed the underlying table since the structure was cached.

## Dependencies And Integration Points

- FTS5 storage calls `sqlite3Fts5IndexIntegrityCheck()` from `fts5_storage.c` after computing the expected checksum over logical table contents.
- Structure handling depends on `fts5StructureRead()`, `fts5StructureDecode()`, `fts5StructureRelease()`, and `fts5StructureInvalidate()` from earlier in `fts5_index.c`.
- Low-level page IO depends on `fts5DataRead()`, `fts5LeafRead()`, `fts5DataRelease()`, `FTS5_SEGMENT_ROWID()`, and `%_idx` SQL prepared through `fts5IndexPrepareStmt()`.
- Iterator integration uses `fts5MultiIterNew()`, `fts5MultiIterNext()`, `fts5MultiIterTerm()`, `fts5MultiIterRowid()`, `fts5MultiIterIsEmpty()`, `fts5SegiterPoslist()`, and `fts5MultiIterFree()`.
- Doclist-index checks and decoding use `fts5DlidxIterInit()`, `fts5DlidxIterNext()`, `fts5DlidxIterPrev()`, `fts5DlidxIterPgno()`, `fts5DlidxIterRowid()`, `fts5DlidxLvlNext()`, and `fts5DlidxIterFree()`.
- Position-list decoding depends on `sqlite3Fts5PoslistNext64()`, `sqlite3Fts5PoslistReaderInit()`, `sqlite3Fts5PoslistReaderNext()`, `FTS5_POS2COLUMN()`, and `FTS5_POS2OFFSET()`.
- SQLite SQL-function and virtual-table APIs are used directly: `sqlite3_create_function()`, `sqlite3_create_module()`, `sqlite3_value_*()`, `sqlite3_result_*()`, `sqlite3_declare_vtab()`, and `sqlite3_index_info`.
- Compile-time gates matter: `SQLITE_DEBUG` enables extra integrity self-tests; `SQLITE_TEST` or `SQLITE_FTS5_DEBUG` enables SQL-facing debug helpers.
- Tests under `ext/fts5/test` reference these helpers heavily, including `fts5rowid.test`, `fts5corrupt*.test`, `fts5fault1.test`, `fts5secure*.test`, and `fts5contentless*.test`.

## Risks And Edge Cases

- Integrity checking sits on a corruption boundary. Most parsing reads varints and offsets from on-disk blobs, so every offset check before using reconstructed terms, doclist ranges, or page-index entries matters.
- `fts5IntegrityCheckPgidx()` must keep the reconstructed previous term consistent with the compressed current term. A missed `nKeep` or `nByte` bound check could turn corrupt disk data into an out-of-bounds read.
- The doclist-index check has secure-delete exceptions. In secure-delete mode, removed rowids can make the first rowid greater than the doclist-index advertised rowid, while non-secure-delete still expects equality.
- `fts5IndexIntegrityCheckSegment()` contains a TODO for proving that no doclist index exists when `%_idx` does not advertise one. Corruption in stray doclist-index records may not be detected by this path.
- The final rightmost-leaf check is disabled with `#if 0`, so the current segment scan does not enforce that the last `%_idx` entry reaches `pSeg->pgnoLast`.
- Debug prefix self-tests are skipped when pending hash data exists, because the hash table supports only one scan query at a time. Bugs that require pending in-memory data may escape this extra debug comparison.
- `fts5TestUtf8()` gates no-index prefix comparisons, but it is deliberately a lightweight validator for test safety rather than a full text subsystem.
- `fts5DecodeFunction()` uses zero padding to reduce overread risk on corrupt records, but debug decoding still trusts many format details enough to be a diagnostic aid, not a hardened parser for untrusted blobs.
- The tombstone decoder reads `aBlob[0]` and `aBlob[1]` after allocation; malformed very-short blobs rely on SQLite value/blob behavior and padding assumptions, so tests should keep exercising corrupt tombstone inputs.
- `fts5structBestIndexMethod()` requires `struct=?`; without it the virtual table returns `SQLITE_CONSTRAINT`. Callers must supply the serialized structure blob explicitly.
- `sqlite3Fts5IndexReset()` assumes `p->iStructVersion` is non-zero when `p->pStruct` is cached. The assertion protects the cache-version contract in debug builds.

## Test Signals

- FTS5 `integrity-check` should pass for populated tables using `detail=full`, `detail=col`, and `detail=none`, with and without prefix indexes.
- Corruption tests should delete or corrupt `%_data` leaf pages, `%_idx` rows, page-index offsets, split keys, doclist-index pages, rowid pointers, and structure records, then verify `SQLITE_CORRUPT_VTAB` or table-specific corruption messages.
- Checksum tests should cover both `bUseCksum` enabled and disabled paths, including mismatches between logical storage checksums and physical index scan checksums.
- Debug builds should exercise ASC/DESC term query parity, prefix-index versus no-index parity, and doclist-index forward/reverse parity.
- Secure-delete tests should cover empty first leaf pages retained in `%_idx`, removed first rowids, detail=none/detail=col secure-delete tables, and version transitions.
- Contentless-delete tests should inspect `fts5_structure` columns for `loc1`, `loc2`, `npgtombstone`, `nentrytombstone`, and `nentry`.
- `fts5_decode()` tests should decode structure row `id=10`, averages records, normal segment leaves, doclist-index rows, tombstone hash pages, and malformed blobs without leaking memory.
- `fts5_decode_none()` tests should cover detail=none leaf pages, rowid-list delete markers, and prefix-compressed terms.
- `fts5_rowid()` tests should verify accepted `segment` calls and the documented error strings for no arguments, wrong arity, and unknown subject.
- Reset/cache tests should change underlying FTS5 data from another statement or connection, call `sqlite3Fts5IndexReset()`, and verify cached structure invalidation before subsequent reads.
