# sources/storage-engines/rocksdb/monitoring/file_read_sample.h

Purpose: Defines lightweight sampling helpers for file-read accounting so RocksDB can estimate read counts without instrumenting every read path at full cost.

Important APIs/types/functions: `kFileReadSampleRate` is 1024. `kFileReadNextSampleRate` is 64 times larger and must remain a power of two. `should_sample_file_read()` uses the thread-local random generator and a fixed hit value; `should_sample_file_read_next()` uses a thread-local counter and bitmask. `sample_file_read_inc()` and `sample_collapsible_entry_file_read_inc()` scale sampled reads into `FileMetaData::stats` atomics.

Control flow: Callers ask whether to sample a read or iterator-next read, with sync-point callbacks able to override the boolean for tests. If sampled, callers increment sampled counters by the base sample rate using relaxed atomics.

State and dependencies: The only local mutable state is the thread-local next-read counter. It depends on `db/version_edit.h` for `FileMetaData`, `util/random.h`, and `test_util/sync_point.h`.

Risks/test signals: Sampling is approximate and intentionally relaxed. `sample_collapsible_entry_file_read_inc()` also adds `kFileReadSampleRate` even though next-read sampling is rarer, so callers must understand the intended estimate semantics. Sync points provide deterministic test hooks.
