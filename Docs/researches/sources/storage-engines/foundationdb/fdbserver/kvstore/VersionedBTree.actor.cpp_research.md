# Research: sources/storage-engines/foundationdb/fdbserver/kvstore/VersionedBTree.actor.cpp

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008475`: lines 1-6744, `Docs/researches/chunks/subset-b-008475_research.md`
- `subset-b-008476`: lines 6745-11091, `Docs/researches/chunks/subset-b-008476_research.md`

## Chunk Research

### subset-b-008475: lines 1-6744

# sources/storage-engines/foundationdb/fdbserver/kvstore/VersionedBTree.actor.cpp lines 1-6744

## Scope

This chunk covers the first 6,744 lines of FoundationDB's Redwood `VersionedBTree.actor.cpp`. It includes support utilities, the pager-internal durable FIFO queue, Redwood metrics and cache infrastructure, the `DWALPager` implementation, page snapshot handling, B-tree record/page encoding helpers, lazy subtree clearing, B-tree initialization, mutation buffering, page splitting/building, and the first part of recursive commit application. The chunk ends inside `VersionedBTree::commitSubtree()` while it is processing internal pages, so root commit completion, reads/cursors, `IKeyValueStore` integration, and most tests are in later chunks.

## Purpose

This portion implements the storage foundation for Redwood: a versioned page pager plus the lower and middle layers of a delta-compressed B-tree. `DWALPager` supplies crash-safe, version-aware logical page access using delayed write-ahead remaps. `VersionedBTree` uses that pager to maintain a sorted key-value tree whose leaves store user records and whose internal pages store lower-bound keys pointing to child page links. The visible commit path turns buffered mutations into page updates, either by editing existing `DeltaTree2` pages in place or rebuilding/splitting pages when edits no longer fit.

## Key Dependencies

- FoundationDB client and flow primitives: `KeyRef`, `ValueRef`, `KeyRangeRef`, `Version`, `Future`, `Promise`, actors, `Arena`, `Reference`, `TraceEvent`, `Histogram`, `PriorityMultiLock`, `FlowLock`, and deterministic simulation helpers.
- Storage interfaces: `IKeyValueStore`, `IPager2`, `IPagerSnapshot`, `ArenaPage`, `PagerCommitHeader`-related page metadata, `EncodingType`, `PageType`, `PagerEvents`, and `PagerEventReasons`.
- Local Redwood structures: `DeltaTree2` from `DeltaTree.h`, `VersionedBTreeDebug.h`, and `ArtMutationBuffer.h`.
- Disk I/O: `IAsyncFile`/`IAsyncFileSystem`, uncached/unbuffered reads and writes, file growth via `truncate()`, and sync-based durability.
- Metrics and configuration: `SERVER_KNOBS`, `FLOW_KNOBS`, `DDSketch`/`Histogram`, and simulator corruption injection.

## Important APIs, Types, and Functions

### Compatibility and Debug Helpers

- `legacyXorWithForPagerName()` and `prepareLegacyXorCompatibility()` preserve legacy test-only XOR page encoding behavior for older simulated Redwood files. The filename hashing behavior intentionally keeps a historical slash-retention quirk so restart/upgrade tests can continue reading old files.
- `addPrefix()` and the overloaded `toString()` helpers provide uniform debug rendering for page IDs, versions, containers, optional values, and queue/map state.
- `ioMinPriority`, `ioLeafPriority`, and `ioMaxPriority` define page I/O priority levels used by pager reads/writes and queue metadata.

### `FIFOQueue<T, Codec>`

`FIFOQueue` is a pager-backed durable queue used both by Redwood and by the pager itself for metadata queues. It stores records in a linked list of physical pages and deliberately avoids versioned/atomic page updates because queue pages are part of the pager's own metadata machinery.

Important nested structures:

- `FIFOQueueCodec<T>` serializes either trivially-copyable values or custom types with `readFromBytes()`, `bytesNeeded()`, and `writeToBytes()`.
- `QueueState` is the persisted header state: queue id, head page and offset, tail page, entry/page counts, extent mode, and extent tail bookkeeping.
- `QueuePage` is the on-page queue header: next page id/offset, end offset, extent position/end, and item-space size.
- `Cursor` drives queue reads and writes with modes `POP`, `READONLY`, and `WRITE`.

Key methods:

- `create()` initializes a new queue at a newly allocated page.
- `recover()` rebuilds queue cursors from persisted `QueueState`.
- `pushBack()`/`pushFront()` append or prepend records; prepends are written to a separate head-writer chain until flush.
- `pop()` reads and removes flushed records, optionally bounded by an inclusive maximum.
- `peek()`, `peekAll()`, and `peekAllExt()` read without consuming records; `peekAllExt()` fast-paths extent-backed queues during remap recovery.
- `preFlush()`, `finishFlush()`, and `flush()` implement durable queue finalization.

Persistence behavior:

- Queue pages are written once before being freed. A flush first links the current data tail to a newly allocated empty tail page, so a later un-synced attempt to append does not corrupt already durable queue data.
- `preFlush()` may allocate a new tail page and must be repeated for mutually dependent pager queues because queue `pop()` can call pager `freePage()` and queue `push()` can call pager `newPageID()`.
- Extent mode packs queue pages into contiguous blocks and tracks extent usage/freeing through `extentCurPageID`, `extentEndPageID`, `extentUsedList`, and `extentFreeList`.

Risks:

- Queue cursor async state is protected by `FlowMutex`; callers must respect `notBusy()`/flush sequencing or metadata state can be persisted too early.
- Extent reads do manual subpage decoding and corruption classification; offset/page-size mistakes would affect cold recovery.
- Queue metadata is deeply tied to pager allocation/freeing, so small ordering changes in `preFlush()` or `finishFlush()` can become crash-consistency bugs.

### `RedwoodMetrics`

`RedwoodMetrics` is a global metrics collector for Redwood page operations and user operations. It tracks:

- Per-level page reads, builds, modifications, commits, lazy clears, forced updates, detached children, and event reasons.
- Pager disk/cache/remap/eviction counters.
- Operation counters for sets, clears, commits, gets, range reads, written/read key-value sizes, and leaf prefetches.
- Histograms for page fill, stored KV fraction, item count, and KV size.

`redwoodMetricsLogger()` periodically logs a `RedwoodMetrics` trace event and resets counters. `redwoodHistogramsLogger()` separately emits histogram samples. `getFields()` and `getIOLockFields()` are declared here and implemented later in the file.

### `ObjectCache<IndexType, ObjectType>`

`ObjectCache` is an intrusive-list LRU-like cache used by pager page and extent caches. The nested `Evictor` owns cross-cache memory accounting and eviction order.

Required object API:

- `evictable()`
- `onEvictable()`
- `cancel()`

Key behaviors:

- `getIfExists()` probes without changing LRU order.
- `get()` creates entries, counts hit/miss behavior by caller intent, and trims through the shared evictor before adding a new entry.
- `prioritizeEviction()` moves an entry into a side list, later restored to the front by `flushPrioritizedEvictions()`.
- `clear()` reclaims all entries from the evictor, waits for safe eviction or cancels, and clears cache storage.

Risks:

- `Evictor::trim()` stops after a bounded number of attempts and can leave cache pressure unresolved if oldest entries are not evictable.
- Moved-out prioritized entries still count against size, so every path must eventually `moveIn()` or `reclaim()`.

### `DWALPager`

`DWALPager` is the visible implementation of `IPager2` in this chunk. It maps logical page IDs to physical page IDs by version so a logical page can be updated atomically without overwriting the prior version immediately. It is effectively a delayed WAL: updated pages are written to alternate physical pages, remap records are persisted, and old/new physical pages are coalesced later after old snapshots expire.

Important persisted queue entry types:

- `DelayedFreePage { version, pageID }`: pages reusable after a version becomes obsolete.
- `RemappedPage { version, originalPageID, newPageID }`: remap, free, or detach entry. `newPageID == invalidLogicalPageID` means free; `newPageID == 0` means detach.
- `ExtentUsedListEntry { queueID, extentID }`: tracks extent-backed queue allocations.

Important pager state:

- `PagerCommitHeader`: persisted in header pages and includes format version, queue count, page size, page count, extent size, committed/oldest versions, user commit record, and queue states.
- `pageCache`: normal page cache keyed by physical/logical page id after remap resolution.
- `extentCache`: temporary non-evicting extent cache used during remap queue recovery.
- `remappedPages`: in-memory `originalPageID -> version -> physical/remap state`.
- `snapshots`: ordered `DWALPagerSnapshot` entries retaining readable versions.
- `operations`: outstanding disk writes that must complete before commit sync.

Key lifecycle flow:

1. Constructor sets cache limits, initializes global metrics lock pointer, starts metrics logging if needed, and launches `recover()`.
2. `recover()` opens or creates the page file, sets header page sizing, then either reads existing headers or initializes a new pager.
3. Existing file recovery tries the primary header, falls back to backup for recoverable primary-header corruption, validates `PagerCommitHeader::FORMAT_VERSION`, recovers all metadata queues, rebuilds `remappedPages` from `remapQueue`, clears temporary extent cache, repairs primary header from backup if needed, restores committed header state, and starts `remapCleanup()`.
4. New file creation initializes header pages, reserves two header pages, creates free/delayed/remap/extent queues, creates an empty initial snapshot, and defers durability to the first commit.
5. `commit()` serializes the next version by writing the prior header to backup, stopping remap cleanup, flushing queues, syncing page writes, writing the new primary header, syncing again, publishing a new snapshot, expiring old snapshots, restarting remap cleanup, and flushing prioritized evictions.

Important APIs:

- `newPageID()` allocates from free list, delayed free list if old enough, or grows the pager.
- `newExtentPageID()` allocates or grows an extent and records it in `extentUsedList`.
- `updatePage()` writes a physical page or multipage and updates cache futures immediately.
- `atomicUpdatePage()` allocates a new page, writes there, appends a `RemappedPage`, updates `remappedPages`, and returns the original logical id.
- `freePage()` either appends a remap-free entry for remapped logical pages or calls `freeUnmappedPage()`.
- `detachRemappedPage()` converts the latest remap into caller-owned physical storage while logging detach semantics.
- `readPage()` and `readMultiPage()` serve latest physical data with cache/probe accounting.
- `readPageAtVersion()` resolves remaps with `getPhysicalPageID()` and reads the physical page for a snapshot version.
- `readExtent()` supports recovery fast-path extent reads for the remap queue.
- `clearRemapQueue()` forces two commits with a zero cleanup window so tests/sanity checks can drain remaps.
- `getUserPageCount()` flushes cleanup/queues and computes user-visible page usage excluding pager metadata queues.

Crash and persistence behavior:

- Two header pages are used. Commit writes the last committed header to backup, syncs all data and backup header, then writes/syncs the primary header for the new version.
- On primary header corruption that can plausibly result from an unsynced write, recovery uses backup. Unsupported format, wrong page id, and backup failure are treated as hard recovery errors.
- `OPEN_ATOMIC_WRITE_AND_CREATE` hides newly created files from directory listings until the first durable primary-header sync.
- Remap cleanup copies alternate physical data back to original logical page locations only after old versions no longer need the old original contents.
- Freed physical pages are delayed when needed so in-flight readers cannot race reuse.

Remap cleanup flow:

- `remapCleanup()` calculates a cleanup window from bytes/page size and tolerance knob, pops remap entries at or below `effectiveOldestVersion()`, and schedules `removeRemapEntry()` tasks.
- `removeRemapEntry()` decides whether to copy new data back, free new id, free original id, or skip based on the current entry and the next logical remap/free/detach state.
- The cleanup run freezes `oldestRetainedVersion` to avoid multiple copy operations to the same original id racing out of order.

Risks:

- Remap cleanup has subtle races with reads, detach, and free. The code explicitly delays freeing `newID` until after `getLastCommittedVersion() + 1` because uncached or just-created cached reads may still hit disk later.
- `updatePage()` mutates cache state before the disk write completes; correctness depends on waiting `operations` during commit and honoring write ordering when a page is already being written.
- `memoryOnly` mode bypasses actual disk I/O but still exercises cache/page semantics; it can fail once cache space is exhausted.
- `readExtent()` computes partial head/tail extent sizes from remap queue header state; this is a recovery-critical path.
- `getPhysicalPageID()` asserts remap lookups do not resolve to `invalidLogicalPageID`; any incorrect remap-free visibility can become a hard crash.

### `DWALPagerSnapshot`

`DWALPagerSnapshot` implements `IPagerSnapshot` for a retained pager version. It forwards physical-page reads through `readPageAtVersion()` or `readMultiPage()` and exposes the snapshot's metadata key/version. Snapshot lifetimes prevent old pages from being reused: `expireSnapshots()` only drops snapshots older than the requested oldest version when their reference is solely held by the pager.

### B-tree Record and Page Encoding

`SplitStringRef` is a small two-segment string helper with comparison and concatenation utilities. It is present as a TODO-adjacent helper; `RedwoodRecordRef` still stores contiguous `KeyRef` plus optional `ValueRef`.

`BTreeNodeLinkRef`/`BTreeNodeLink` encode one logical B-tree page as a vector of one or more logical pager page IDs. Multipage B-tree nodes are represented by concatenating these physical pages.

`RedwoodRecordRef` represents both leaf records and internal boundary records:

- Leaf: `key` plus optional value.
- Internal: boundary key plus `value` containing a serialized `BTreeNodeLinkRef`.
- Null internal records have no value and preserve decode boundaries after subtree deletion.

Important methods:

- `getChildPage()`, `setChildPage()`, and `withPageID()` manipulate internal links.
- `withoutValue()` keeps the key as a boundary without a child/value.
- `withMaxPageID()` creates a high sentinel child value.
- `compare()`, relational operators, and `sameExceptValue()` order records by key and value presence.
- `deltaSize()` and `writeDelta()` support `DeltaTree2` encoding.

`RedwoodRecordRef::Delta` is the packed delta format used by `DeltaTree2`:

- One flags byte records prefix source, deletion flag, value presence, and length-format selector.
- Four compact length formats cover common small prefix/suffix/value lengths and rarer larger values.
- Serialized bytes store value bytes followed by key suffix bytes.
- `apply()` reconstructs a record from a base record or cached key prefix.

`DeltaValueOnly` is a decode specialization used when only child links/values are needed, notably lazy clearing, so key decoding can be skipped.

`BTreePage` wraps a delta tree with page metadata:

- `treeOffset`, `height`, and `kvBytes`.
- `tree()` for full record decoding and `valueTree()` for value-only decoding.
- `isLeaf()` identifies leaf height `1`.
- `toString()` renders decoded page contents and annotates records outside decode bounds, which can happen after subtree deletion/incremental insertion.

### `DecodeBoundaryVerifier`

This simulation-only verifier records decode lower/upper bounds by page id and version at write time and checks later reads use compatible boundaries. It also samples boundaries and optionally scans domain-prefix constraints. It is disabled after simulation restarts because old writes were not captured.

Important methods:

- `update()` records written page boundaries.
- `verify()` checks read-time boundaries against the recorded write.
- `updatePageId()` carries boundary metadata from old to newly allocated page ids.
- `removeAfterVersion()` drops verifier data beyond recovered committed version after restart/recovery.

### `VersionedBTree` State and Public Surface in This Chunk

Visible public operations:

- `set(KeyValueRef)` buffers a set mutation and updates metrics.
- `clear(KeyRangeRef)` buffers a point clear or range clear.
- `setOldestReadableVersion()`, `getOldestReadableVersion()`, and `getLastCommittedVersion()` bridge to pager version state.
- `init()` waits for `init_impl()`.
- `commit(Version)` chains commits through `m_latestCommit`.
- `clearAllAndCheckSanity()` destructively clears the tree, drains lazy clears/remaps, and asserts minimal page usage.
- `close()`/`dispose()` destroy the B-tree and close/dispose the owned pager.

Important persisted tree header:

- `BTreeCommitHeader` with format version, encoding type, tree height, lazy-delete queue state, root link, and deprecated encryption mode field.
- Root pointer size is bounded because it lives in the pager commit record/header path.

Core state:

- `m_pager`: owned pager.
- `m_pBuffer`: current mutation buffer.
- `m_header`: persisted B-tree metadata.
- `m_lazyClearQueue`: durable queue of internal subtrees to delete after range clears.
- `childUpdateTracker`: tracks child page updates so parent-level write optimizations can be made later.
- `m_pDecodeCacheMemory`: page-cache penalty source used by delta decode caches.
- `m_pBoundaryVerifier`: simulation-only boundary verifier.

Initialization flow:

- `init_impl()` waits for pager recovery, creates a fresh mutation buffer, reads pager commit record, and either creates a new B-tree or recovers an existing one.
- New tree creation allocates an empty leaf root page, writes it through the pager, creates the lazy-clear queue, and serializes initial tree header state.
- Existing tree recovery validates `BTreeCommitHeader::FORMAT_VERSION`, enforces or adopts encoding type for legacy simulated XOR pages, and recovers the lazy-clear queue.

### Mutation Buffer

Mutations are represented as ordered range boundaries:

- `RangeMutation` records whether the boundary key itself changes, what value it should have if set, and whether the range after the boundary is cleared.
- `SingleKeyMutation` models clear, set, and atomic operation shape, although atomic ops must be coalesced before converting to a record in this visible chunk.
- `MutationBufferStdMap` is a simple `std::map<KeyRef, RangeMutation>` implementation with permanent `dbBegin` and `dbEnd` sentinels.
- `MutationBufferART` from `ArtMutationBuffer.h` is selected by `USE_ART_MUTATION_BUFFER`.

`set()` inserts a boundary and sets a boundary value. `clear()` creates either a point clear boundary or a range clear by setting the begin boundary to clear-all, inserting the end boundary, and erasing intermediate buffered mutations.

### Lazy Clear

`LazyClearQueueEntry` records `{ height, version, pageID }` for deleted internal subtrees. `incrementalLazyClear()` pops a bounded number of internal pages, reads each page at the latest committed snapshot, and either frees leaf children directly or queues lower internal children. It finally frees the queued internal page itself.

Lazy clear is used so large subtree deletes do not synchronously traverse and free every descendant during the foreground mutation merge. The queue is persisted via the B-tree header and pager queue state.

Risks:

- Lazy clear assumes level-1 leaf nodes are never queued.
- It reads with the latest committed pager snapshot and frees at the queued version. Incorrect version pairing would risk freeing pages visible to old snapshots.
- Value-only decoding intentionally skips keys; it depends on internal page values accurately encoding child page links.

### Page Splitting and Building

`PageToBuild` models a future B-tree page while scanning records:

- Tracks record range, page size, bytes left, block count, KV bytes, height, and whether the embedded `DeltaTree2` has crossed the large-tree threshold.
- `addRecord()` adds a record or grows page size by base blocks when forced.
- `shiftItem()` moves a record between adjacent page plans to reduce slack.

`splitPages()` computes page plans for a set of records between lower/upper bounds:

- Leaf pages can have one large record; internal pages target at least four records.
- Delta sizes are computed against lower bound, previous record, or upper bound with worst-case overhead.
- Slack and distribution knobs control when pages are finalized and whether the final two pages are balanced.
- Simulation sometimes disables final balancing to exercise underfilled-page cases.

`writePages()` builds one or more `BTreePage`s from records:

- Computes shared prefix length from lower/upper bounds.
- For leaf splits, shortens non-last upper boundaries to the shortest distinguishing prefix.
- For internal pages, handles null child records that exist only to preserve decode boundaries.
- Creates an `ArenaPage`, initializes it as `BTreeNode` or `BTreeSuperNode`, builds the embedded `DeltaTree2`, samples metrics, and writes through the pager.
- If the rebuild results in a single one-block page replacing a single one-block old page, it uses `atomicUpdatePage()` to preserve logical id; otherwise it allocates fresh page ids, writes the new page(s), and frees old ids once.
- Returns boundary records whose values point at the newly written child page links.

`buildNewRootsIfNeeded()` repeatedly writes new root levels until there is exactly one root record, the root pointer fits in the commit record, and the root lower key is `dbBegin`.

### Read and Update Helpers

- `readPage()` reads one-page or multipage B-tree nodes through an `IPagerSnapshot`, updates read metrics, and returns an `ArenaPage`.
- `getCursor()` creates or reuses a `DeltaTree2::DecodeCache` from decode bounds, optionally storing it in `page->extra` for higher pages.
- `preLoadPage()` issues cacheable prefetch reads for range scans and updates preload metrics.
- `freeBTreePage()` frees each pager page in a B-tree node link and erases parent update-tracking state for internal pages.
- `updateBTreePage()` writes a modified page, using atomic update for one-block nodes or allocating/freing multipage node links otherwise.
- `clonePageForUpdate()` clones a page and preserves its decode cache pointer for mutation.

### `commitSubtree()` Visible Flow

The chunk includes leaf-page commit logic and the beginning of internal-page recursion.

Leaf-page logic:

1. Read the current subtree root page at the batch snapshot.
2. Create a cursor using the update's decode bounds.
3. Decide whether to try in-place `DeltaTree2` updates. It only tries when the page is non-empty and logical/decode boundaries are normal.
4. Walk mutation-buffer ranges from `mBegin` to `mEnd`.
5. For each boundary, apply set/clear behavior:
   - Same-sized value replacement can memcpy directly into the cloned page.
   - Existing records can be erased in update mode or skipped in rebuild mode.
   - Insert attempts use `cursor.insert()` until unbalance/space limits fail.
6. If insertion fails, switch from update mode to a linear merge vector and later rebuild pages.
7. For clear ranges, either seek past removed data or erase visited records depending on update/rebuild mode.
8. If no actual change was made, return without parent-visible changes.
9. If update mode emptied the page, free it and mark the subtree as cleared.
10. If update mode succeeded, write the updated page with `updateBTreePage()` and mark the slice updated in place.
11. If rebuild mode produced no records, free the page and mark the slice cleared.
12. Otherwise call `writePages()` and mark the slice rebuilt.

Internal-page preparation:

- `InternalPageSliceUpdate` describes a child subtree range, distinguishing logical subtree bounds from decode bounds. It tracks whether child links changed, rebuilt links, expected upper boundary, and whether the update happened in place.
- `InternalPageModifier` applies ordered child-slice updates to an internal page, either editing the existing delta tree or switching to rebuild-vector mode if insertion fails.
- At the end of this chunk, `commitSubtree()` is iterating internal child links, building slice descriptors, handling null dummy records used for decode boundaries, computing mutation buffer ranges for each slice, and detecting uniformly cleared or unchanged subtree spans to avoid recursion. The rest of internal recursion and parent/root assembly is outside this chunk.

## Control Flow Summary

Pager startup:

1. `DWALPager` construction starts `recover()`.
2. Recovery opens/creates the file, validates or initializes headers, recovers metadata queues, and reconstructs in-memory remaps.
3. A readable snapshot is installed at the committed/recovered version.
4. `VersionedBTree::init_impl()` reads the pager commit record and creates or recovers B-tree metadata.

Mutation write path visible here:

1. `set()` and `clear()` add ordered boundaries to `m_pBuffer`.
2. `commit()` chains to `commit_impl()` in later code, but visible helpers show it constructs `CommitBatch` state and uses `commitSubtree()` to apply buffered ranges.
3. `commitSubtree()` reads affected pages, edits or rebuilds them, reports child-link changes upward, and frees replaced/deleted pages at the write version.
4. `writePages()` and `updateBTreePage()` call pager `atomicUpdatePage()` or allocate/write/free page ids.
5. Pager commit persists page writes, queue state, B-tree header commit record, and version metadata.

Cleanup path:

1. B-tree subtree clears enqueue internal pages to `m_lazyClearQueue`.
2. `incrementalLazyClear()` gradually frees descendants.
3. Pager `remapCleanup()` gradually collapses versioned remaps after old snapshots expire.
4. Sanity/test helpers can force lazy clear and remap cleanup to drain.

## State and Persistence Behavior

- Pager metadata durability is rooted in `PagerCommitHeader` persisted in primary and backup header pages.
- B-tree metadata durability is rooted in `BTreeCommitHeader` serialized into the pager's user commit record.
- `FIFOQueue::QueueState` persists pager free lists, delayed free lists, extent lists, remap queue, and B-tree lazy-clear queue.
- Page versions are retained through pager snapshots. `effectiveOldestVersion()` is the min of committed oldest readable version and the oldest live snapshot.
- B-tree page contents are encoded as `ArenaPage` payloads containing `BTreePage` plus `DeltaTree2` records. Leaf and internal pages share record encoding; internal values are page-link byte vectors.
- Multipage B-tree nodes are supported by storing a vector of logical page IDs as a single node link.
- Decode caches are transient memory and can be stored in `ArenaPage::extra`; their memory is charged through the pager cache penalty source.

## Integration Points

- `VersionedBTree` owns an `IPager2` and depends on pager snapshots for versioned reads and pager commits for durable version publication.
- `KeyValueStoreRedwood` and public `IKeyValueStore` methods are below this chunk, but this code is the underlying engine they will wrap.
- `ArtMutationBuffer.h` is included directly inside `VersionedBTree` and selected as the active mutation buffer.
- `DeltaTree2` is the core encoded-node storage; all page edits/builds depend on its cursor, build, insert, erase, and decode-cache APIs.
- Flow actors and `Future` composition drive asynchronous disk reads/writes, queue operations, recovery, lazy cleanup, and remap cleanup.
- Simulation hooks (`buggify`, deterministic random, corruption injection, boundary verifier) intentionally perturb page sizes, split balancing, and corruption paths to improve test coverage.

## Risks and Edge Cases

- Crash consistency depends on precise ordering among queue flushes, page writes, backup header sync, primary header write, and final sync.
- `FIFOQueue` self-dependency with pager allocation/freeing is subtle; flush loops must handle work generated by earlier flush operations.
- Remap cleanup must not free pages still reachable by live snapshots or in-flight uncached disk reads.
- Internal page dummy/null records are required to preserve delta decode boundaries after subtree deletion. Dropping or misplacing them can make later page decoding impossible even if logical key ranges look correct.
- In-place `DeltaTree2` edits are opportunistic. When inserts fail, the code switches to rebuild mode and must replay already visited records correctly.
- Same-size value memcpy updates mutate the page data directly after cloning; this optimization depends on cursor value references pointing into the cloned page after `switchTree()`.
- Multipage B-tree nodes trade parent rewrites against atomic updates. Incorrect free/allocation handling for old multipage links could leak or prematurely reuse pages.
- Format versions are hard gates: pager format version `10` and B-tree format version `17` must match exactly.
- Legacy XOR compatibility is simulation/test-only but affects recovery of older test files.

## Test Signals Visible in This Chunk

- `TraceEvent`s: `RedwoodRecoveredPager`, `RedwoodRecoveredBTree`, `RedwoodMetrics`, `RedwoodRecoveryErrorPrimaryHeaderFailed`, `RedwoodRecoveryErrorBackupHeaderFailed`, `RedwoodRecoveryFailedWrongVersion`, `RedwoodPageSizeMismatch`, `RedwoodPageError`, `RedwoodChecksumFailed`, `RedwoodQueueNumEntriesMisMatch`, `RedwoodBTreeVersionUnsupported`, `RedwoodBTreeUnexpectedEncodingType`, `RedwoodDeltaTreeOverflow`, `RedwoodClearRemapQueue`, and `RedwoodDestructiveSanityCheck`.
- Assertions validate page heights, queue entry counts, format versions, remap invariants, non-empty page links, lazy-clear height constraints, and page split/build bounds.
- Simulation-only mechanisms intentionally reduce queue item space, force occasional page splits, disable balancing, vary cleanup tolerance, inject corruption, and validate decode boundaries.
- `clearAllAndCheckSanity()` is an explicit destructive sanity path: clear all keys, repeatedly commit until lazy clear is drained, drain remaps, then assert exactly two user pages remain: root plus lazy-delete queue page.
- Metrics counters and histograms provide operational signals for cache hits/misses, remap cleanup, page build/modify/read counts, lazy-clear requeue/free counts, page fill/stored percentages, and KV sizes.

## Open Cross-Chunk References

- `commit_impl()` for `VersionedBTree`, read cursors/range APIs, `KeyValueStoreRedwood`, unit tests, and detailed metrics field rendering are outside this chunk.
- `commitSubtree()` continues beyond line 6,744; this report covers the visible leaf update path and the start of internal-page slice planning but not the complete recursive internal commit assembly.
- The active `MutationBufferART` implementation is included from `ArtMutationBuffer.h`; only the fallback `MutationBufferStdMap` shape is fully visible in this chunk.

### subset-b-008476: lines 6745-11091

# sources/storage-engines/foundationdb/fdbserver/kvstore/VersionedBTree.actor.cpp lines 6745-11091

## Scope

This chunk covers the end of `VersionedBTree::commitSubtree`, the top-level B-tree commit actor, the public B-tree cursor used for point and range reads, the `KeyValueStoreRedwood` `IKeyValueStore` adapter, Redwood metrics formatting, and a large block of unit, correctness, and performance tests for Redwood's page, delta-tree, queue, insert, seek, and range-scan behavior. Earlier chunks define most page formats and helper types used here; this chunk shows how those pieces are committed, read, exposed through the storage-engine interface, and stressed.

## Purpose

The production code in this range closes the write path and exposes the read path:

- recursive commit processing turns mutation-buffer ranges into leaf/internal page updates, subtree clears, page rebuilds, remapped child detaches, root replacement, lazy-delete queue state, and pager commits;
- `BTreeCursor` gives snapshot-backed seek and bidirectional iteration over Redwood records, including page descent, sibling prefetch, cursor reuse, and arena lifetime handling for reads;
- `KeyValueStoreRedwood` adapts `VersionedBTree` to FoundationDB's `IKeyValueStore` contract for initialization, close/dispose, commit, set/clear, point read, prefix read, range read, error propagation, and storage-byte reporting.

The test and benchmark code in the same chunk provides direct validation signals for the lower-level delta encoding, `DeltaTree`/`DeltaTree2` mutation and seek semantics, full B-tree randomized correctness, restart recovery, page-cache cleanup, extent queue recovery, and several write/read workload shapes.

## Important APIs, Types, and Functions

- `VersionedBTree::commitSubtree(...)`: in this chunk, the internal-page branch builds `InternalPageSliceUpdate` objects per child range, avoids recursion for uniformly cleared or unchanged mutation spans, recursively commits changed children, then uses `InternalPageModifier` to patch, rebuild, or delete the parent page. It frees level-2 leaf children immediately for cleared ranges and queues deeper subtree deletion via `m_lazyClearQueue`.
- `VersionedBTree::commit_impl(Version writeVersion, Future<Void> previousCommit)`: owns a `CommitBatch`, swaps out the mutable mutation buffer, waits for prior commit serialization, sets the new oldest readable version, commits the whole root range, rebuilds the root if needed, stops and flushes lazy clearing, writes the commit header through the pager, and restarts incremental lazy clearing.
- `VersionedBTree::BTreeCursor`: snapshot cursor with a stack of `PathEntry` objects. Public operations include `init`, `seek`, `seekGTE`, `seekLT`, `moveNext`, `movePrev`, `prefetch`, `get`, `back`, `popPath`, and `toString`.
- `VersionedBTree::initBTreeCursor(...)`: obtains an `IPagerSnapshot`, parses or reuses the commit header's root pointer from snapshot metadata, and initializes the cursor at the root.
- `KeyValueStoreRedwood`: the `IKeyValueStore` implementation for `SSD_REDWOOD_V1`. It constructs a `DWALPager`, owns `VersionedBTree`, and translates interface calls to tree calls.
- `KeyValueStoreRedwood::readRange_impl(...)`: performs forward or reverse range reads with cursor seeks, optional sibling prefetch, row/byte limit accounting, page-bound checks, and arena dependency retention.
- `KeyValueStoreRedwood::readValue_impl(...)` and `readValuePrefix_impl(...)`: perform point lookup and optional value truncation while preserving page arena lifetime for the returned `Value`.
- Random/test helpers: `randomSize`, `randomString`, `randomKV`, `verifyRangeBTreeCursor`, `seekAllBTreeCursor`, `verify`, `randomReader`, `IntIntPair`, `deltaTest`, `randomRedwoodRecordRef`, `getDefaultKeyGenerator`, `commitAndReportCorrectnessProgress`, `commitAndReportLoadProgress`, `randomSeeks`, `randomScans`, `KVSource`, `getStableStorageBytes`, `prefixClusteredInsert`, `sequentialInsert`, `closeKVS`, `doPrefixInsertComparison`, and `randomRangeScans`.
- Metrics functions: `RedwoodMetrics::getFields` and `RedwoodMetrics::getIOLockFields` format global operation counters, per-level page counters, event counters, page/decode cache sizes, and IO lock active/waiting counts into either `TraceEvent` fields or human-readable strings.

## Control Flow

The internal-page portion of `commitSubtree` walks child records with a page cursor. For each logical child slice, it computes lower/upper subtree boundaries, decode boundaries, expected boundary records, and the mutation-buffer interval that can affect that subtree. If exactly one mutation range covers the slice and its overlap is uniformly clear or uniformly unchanged, the code skips recursion. Uniform clears mark the slice cleared and either free direct child leaf pages or enqueue lazy subtree deletion for deeper pages. Otherwise, the function recurses into the child page with the narrowed mutation range.

After all recursive calls complete, the parent reconstructs its page state using `InternalPageModifier`. Updates are applied in slice order, with the next slice boundary or the caller-provided upper boundary used to preserve decode boundaries. If multiple children were updated in place under this parent, the parent may be force-rewritten so child links can be detached from pager remaps. Depending on modifier state, the parent page is cleared and freed, updated in place through `updateBTreePage`, or rebuilt/split through `writePages`. Rebuild/update results are reflected in the caller's `InternalPageSliceUpdate`.

`commit_impl` serializes commits by waiting on `previousCommit`, treats repeated write versions with no mutations as no-ops, takes a read snapshot at the previous committed version, and commits from the root link over `[dbBegin, dbEnd)`. If `commitSubtree` changes the root, it writes a new empty root for a fully deleted tree or builds new root levels when the returned child-link records no longer fit in the old root. It then stops the lazy clear actor, waits for completed lazy frees, flushes the lazy clear queue, persists the updated commit header through `m_pager->commit`, increments commit metrics, and restarts lazy clearing.

`BTreeCursor::seek_impl` always descends from the root path entry. Internal pages are searched with `query.withMaxPageID()` and `seekLessThan`; null-child boundary records terminate the search as absent. Leaf pages seek the exact `RedwoodRecordRef` query and set cursor validity only for non-erased entries. `move_impl` first walks within or up the current path until it can move to a next/previous internal link, then descends to the leftmost or rightmost leaf record in that direction, skipping internal dummy records that have no child page.

`readRange_impl` chooses forward behavior for positive `rowLimit` and reverse behavior for negative `rowLimit`. It seeks once, optionally calls `BTreeCursor::prefetch`, then drains the current leaf cursor directly without awaiting per record. Page bounds avoid per-key end checks when the entire leaf is inside the requested range. When a page contributes results, the result arena depends on both the delta-tree decode arena and the `ArenaPage` arena. The scan stops when the row limit, byte limit, range bound, root boundary, or current leaf boundary is reached.

## State and Persistence Behavior

Commit state is versioned and pager-backed. `commit_impl` moves the mutable `MutationBuffer` into a `CommitBatch`, resets in-memory mutation count, records `writeVersion`, `readVersion`, and `newOldestVersion`, and updates `m_header.root`, `m_header.height`, and `m_header.lazyDeleteQueue` before committing the header as the pager commit record. The B-tree root is a `BTreeNodeLink`; empty-tree replacement allocates a new page ID and writes an empty height-1 root.

Page persistence is copy-on-write unless the code elects an in-place page update. Internal nodes may be rewritten just to detach remapped child page IDs after enough children have been updated in place. `detachRemappedPage` translates logical remaps to physical page IDs at the commit version and updates the optional `DecodeBoundaryVerifier`. Cleared subtrees are either synchronously freed at leaf-child height or deferred through `m_lazyClearQueue` for incremental background deletion. The commit path stops and drains lazy clearing before persisting the queue state, then restarts `incrementalLazyClear`.

Read state is snapshot isolated. `BTreeCursor` stores an `IPagerSnapshot` and path stack; page records are only guaranteed until cursor movement changes pages. Returned `RangeResult` and `Value` objects explicitly depend on page/decode arenas so zero-copy record references remain valid for the caller. `initBTreeCursor` caches the root link in `snapshot->extra` after parsing the commit metadata key, avoiding repeated commit-header decoding for the same snapshot.

`KeyValueStoreRedwood::commit` uses a monotonically increasing `m_nextCommitVersion`, forwards errors into `m_errorPromise`, and immediately advances oldest readable version to the committed version because this adapter does not keep history. `shutdown` coordinates simulation-only destructive sanity checks, cancellation, close/dispose, and final `m_closed` signaling.

## Dependencies and Integration Points

The code depends on earlier `VersionedBTree.actor.cpp` definitions for `RedwoodRecordRef`, `BTreePage`, `BTreeNodeLinkRef`, `InternalPageSliceUpdate`, `InternalPageModifier`, `MutationBuffer`, `RangeMutation`, `writePages`, `updateBTreePage`, `makeEmptyRoot`, `buildNewRootsIfNeeded`, `readPage`, `preLoadPage`, `DecodeBoundaryVerifier`, and Redwood metrics. It also uses Flow actor primitives (`ACTOR`, `Future`, `Promise`, `PromiseStream`, `wait`, `co_await`, `choose`, `waitNext`), FoundationDB containers/arena types, and deterministic test randomness.

The storage integration point is `keyValueStoreRedwoodV1`, which returns `KeyValueStoreRedwood` for `KeyValueStoreType::SSD_REDWOOD_V1`. Production operation relies on `DWALPager` for page allocation, snapshots, reads, updates, commits, extent queues, remap cleanup, page cache accounting, and close/dispose. Read operations integrate with `ReadOptions`, `ReadType::FETCH`, `PagerEventReasons`, IO priorities, `PriorityMultiLock`, and global Redwood metrics/histograms.

Test code integrates with FoundationDB's `TEST_CASE` framework and parameter system. It compares Redwood against the in-memory `written` version map, optionally compares storage behavior against SQLite (`SSD_BTREE_V2`) in prefix-size workloads, and uses `DecodeBoundaryVerifier` samples to target node-boundary clear ranges. Performance tests expose tunables such as page size, extent size, page cache size, remap cleanup window, concurrency, record counts, scan widths, and read limits.

## Risks and Edge Cases

- Internal dummy boundary records are subtle: cursor seek/move and commit-slice boundary code must skip null-child records in the right places while still preserving decode boundaries. Mistakes can make ranges unreadable or corrupt parent/child boundary invariants.
- The mutation-range shortcut in `commitSubtree` assumes one mutation range uniformly clears or leaves the subtree unchanged. Boundary-key handling around `subtreeLowerBound` decides whether the boundary record itself matters; off-by-one errors here can drop or resurrect a key.
- In-place updates plus pager remapping require parent rewrites and child detaches. If `parentInfo` is stale after awaits, or if large multi-page nodes are detached incorrectly, parent links can point at old remapped pages. The code explicitly reacquires `parentInfo` after recursion waits and skips multi-page node detaches.
- Lazy clearing is part of durable state. Failing to stop, wait, flush, and persist `m_lazyClearQueue` before the pager commit could leak pages or lose pending subtree deletion work across restart.
- `BTreeCursor` returns record references into page/decode arenas. Read paths must keep arena dependencies whenever returning values outside the cursor's lifetime; missing dependencies would become use-after-free bugs.
- Reverse range reads use negative `rowLimit` and increment it toward zero. Incorrect limit handling can report wrong `more` flags or overrun caller byte/row budgets.
- `KeyValueStoreRedwood::commit` advances oldest readable version immediately, so this adapter is not a historical MVCC store. Callers expecting old snapshots through this interface would be incompatible.
- Several benchmark/test loops are intentionally huge (`10e6`, `80e6`, `100e6`, `1e9` defaults). They are useful for manual performance work but too expensive for ordinary quick validation unless parameters are reduced.
- Some tests rely on destructive file deletion, cold restarts, and optional destructive sanity checks. They should run only against disposable test files.

## Test and Validation Signals

This chunk contains direct test coverage:

- `/redwood/correctness/unit/RedwoodRecordRef` validates child-page encoding/copying, delta size/write/apply behavior, common-prefix comparisons, and microbenchmarks for delta encoding and comparison.
- `Lredwood/correctness/unit/deltaTree/RedwoodRecordRef` and `RedwoodRecordRef2` validate `DeltaTree` and `DeltaTree2` record storage, existing-key insert failure, erase/reinsert behavior, forward/reverse/value-only iteration, and high-volume seek behavior.
- `Lredwood/correctness/unit/deltaTree/IntIntPair` cross-checks `DeltaTree` and `DeltaTree2` with a simpler comparable type, covering growth until full, deletions, seek LTE/GTE exact and adjacent cases, hinted seeks, and seek performance variants.
- `:/redwood/performance/mutationBuffer`, `:/redwood/pager/ArenaPage`, and `:/redwood/performance/extentQueue` exercise mutation-buffer insert/lookup/erase, arena-page ownership dependencies, and FIFO extent-queue persistence/recovery paths.
- `Lredwood/correctness/btree` is the main randomized B-tree correctness test. It generates sets and range clears across versions, verifies point and range reads against an external version map, randomly advances oldest readable version, injects cold restarts, optionally runs concurrent random readers, then performs `clearAllAndCheckSanity`.
- `:/redwood/performance/set`, `:/redwood/performance/prefixSizeComparison`, `:/redwood/performance/sequentialInsert`, `:/redwood/performance/randomRangeScans`, and `:/redwood/performance/histograms` provide load, seek, scan, storage-size, and metrics-formatting performance signals.

For focused validation after changing this area, the highest-signal tests are the randomized B-tree correctness test with reduced limits, the delta-tree unit tests, and a range-read workload that covers both positive and negative row limits with byte limits and prefetch enabled. Restart/cold-start paths should be included for changes touching commit header, root rebuild, lazy delete queue, or pager remapping behavior.

## Unresolved Cross-Chunk References

This chunk starts after the leaf-page branch of `commitSubtree` has already begun, so the complete mutation merge and leaf rebuild logic lives in the previous chunk. Key type definitions and helper implementations for `InternalPageSliceUpdate`, `InternalPageModifier`, `writePages`, `buildNewRootsIfNeeded`, `readPage`, lazy clearing, page formats, and metrics structs also begin earlier. The final per-file merge should connect those earlier definitions with this chunk's commit completion, cursor, adapter, and test coverage.
