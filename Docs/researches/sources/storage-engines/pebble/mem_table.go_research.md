# sources/storage-engines/pebble/mem_table.go

Purpose: this file implements Pebble's mutable in-memory LSM component. A `memTable` stores point keys, range deletion tombstones, and range keys in arena-backed skiplists; supports concurrent application of prepared batches; exposes flushable iterators; and caches fragmented range spans.

Important APIs/types/functions: `memTableEntrySize` estimates arena usage. `newMemTable` and `init` configure comparer functions, arena buffer, skiplists, writer refs, caches, and log sequence number. `prepare` reserves memory and adds a writer ref; `apply` inserts batch records with sequence numbers. Iterator APIs include `newIter`, `newFlushIter`, `newRangeDelIter`, and `newRangeKeyIter`. State/size APIs include `readyForFlush`, `availBytes`, `inuseBytes`, `totalBytes`, `empty`, and `computePossibleOverlaps`. Span caching uses `keySpanFrags`, `constructSpan`, `rangeDelConstructSpan`, and `keySpanCache`.

Control flow: batch application checks the batch sequence number against `logSeqNum`, iterates records, constructs internal keys, and routes range deletes to `rangeDelSkl`, range keys to `rangeKeySkl`, log data to no storage/no seq advance, and point mutations to the point skiplist. After insertion it verifies count/sequence consistency and invalidates span caches when range spans were added. Range span iterators lazily call `keySpanCache.get`, which fragments all raw spans through `keyspan.Fragmenter` exactly once per cache generation using `sync.Once`.

State and persistence behavior: the memtable owns a fixed manual arena buffer until `free`. It is append-only; deletes are represented as internal tombstone records. `reserved` pessimistically tracks committed and inflight memory, while `writerRefs` prevents flushing until queued/inflight writers finish. Span caches are atomic and may be populated from a superseded generation, which is acceptable because counts only increase.

Dependencies and integration points: integrates with `Batch`, `flushable`, commit pipeline writer refs, manual memory accounting, `arenaskl`, range deletion/key encoders, comparer split/equality functions, and overlap computation. Flush and iterator paths consume its internal iterators.

Risks and test signals: risks include memory reservation drift, incorrect writer-ref transitions, sequence-number/count mismatches, cache invalidation races, and misclassification of range-key vs range-delete spans. Invariant checks guard range-deletion iterators from accidentally containing range-key kinds.
