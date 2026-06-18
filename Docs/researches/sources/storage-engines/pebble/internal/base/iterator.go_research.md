# sources/storage-engines/pebble/internal/base/iterator.go

Purpose: Defines the internal iterator contract, top-level iterator abstraction, seek flag bitsets, and iterator block-read/statistics aggregation.

APIs and types: `InternalIterator`, `InternalIteratorWithKVMeta`, `TopLevelIterator`, `SeekGEFlags`, `SeekLTFlags`, `BlockReadStats`, and `InternalIteratorStats` with string and redact formatting.

Control flow and state: The interface documents absolute and relative positioning rules, prefix iteration mode, bound enforcement responsibilities, error accumulation, and close semantics. `SeekGEFlags` encodes `TrySeekUsingNext`, `RelativeSeek`, and `BatchJustRefreshed`; `SeekLTFlags` encodes `RelativeSeek`. Stats accumulate block byte/count metrics and merge across iterators.

Persistence and dependencies: No durable state; it standardizes runtime iteration state and stats. Depends on context, time, blockkind categories, humanize formatting, redact formatting, and tree-step introspection.

Integration points: Implemented by memtable, batch, sstable, level, merging, and compaction iterators. Public `Iterator` and compaction code rely on its bound and error contracts.

Risks: Bounds are partly caller-enforced, so incorrect caller positioning can produce out-of-bound results. Prefix iteration prohibits some reverse movement. Lazy values may return errors not included in iterator `Error`.

Test signals: `iterator_test.go` verifies seek flag bit composition and string behavior; behavioral iterator conformance is tested by concrete iterator packages.
