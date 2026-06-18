# sources/storage-engines/rocksdb/file/file_prefetch_buffer.h

## Purpose
`file_prefetch_buffer.h` declares RocksDB's `FilePrefetchBuffer`, `ReadaheadParams`, `BufferInfo`, and usage enum. Together they define the in-memory state machine used to serve file reads from prefetched buffers and to drive synchronous/asynchronous readahead.

## Important APIs and types
`ReadaheadParams` carries initial and maximum readahead sizes, implicit-auto-readahead flags and counters, and `num_buffers`. `BufferInfo` owns an `AlignedBuffer`, offset, async request length, async in-progress flag, filesystem IO handle/deleter, and initial end offset. It provides predicates for whether data or pending async ranges cover an offset, whether buffers are outdated, and current size.

`FilePrefetchBufferUsage` classifies stat attribution for table-open tail prefetch, user scan prefetch, compaction prefetch, and unknown use.

`FilePrefetchBuffer` exposes `Prefetch()`, `PrefetchAsync()`, `TryReadFromCache()`, `min_offset_read()`, `GetPrefetchOffset()`, read-pattern updates, readahead state export, readahead decrement, async callback, and test buffer-inspection methods. Private methods handle buffer preparation, abort/poll, outdated data clearing, internal prefetch, sync/async reads, overlap copying, eligibility logic, FS-buffer use, read-ahead tuning, stats, and active/free buffer queue management.

## State, dependencies, and integration
State is a deque of active buffers, a deque of free buffers, an optional overlap buffer, readahead sizing/counters, previous read pattern, explicit-prefetch state, filesystem/clock/stats pointers, usage, callback, and buffer count. The destructor aborts pending IO, destroys IO handles, records discarded bytes, and deletes all buffers.

## Risks and test signals
The header reveals complex ownership: raw `BufferInfo*` objects move between deques and must be deleted exactly once, async handles must be destroyed through provider deleters, and overlap buffers are allocated only for multi-buffer or FS-buffer cases. `GetPrefetchOffset()` assumes at least one active buffer. Implicit auto-readahead depends on sequential access accounting. Tests should validate constructor/destructor lifecycle, zero/one/multi-buffer cases, min-offset tracking when disabled, buffer queue transitions, and stats for discarded/useful/prefetched bytes.
