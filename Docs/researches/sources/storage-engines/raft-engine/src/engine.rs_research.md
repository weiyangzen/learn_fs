# sources/storage-engines/raft-engine/src/engine.rs

## Purpose
Implements raft-engine's main public storage engine: opening and recovering file logs, writing batches, reading entries and messages through memtables, compacting, purging, syncing, dumping, consistency checking, unsafe repair, metrics flushing, and cached entry decoding.

## Important APIs, Types, And Functions
`Engine<F, P>` owns config, listeners, stats, memtables, pipe log, purge manager, write barrier, and metrics flusher. Key APIs include `open`, `open_with_listeners`, `open_with_file_system`, `open_with`, `write`, `sync`, `get_message`, `get`, `scan_messages`, `scan_raw_messages`, `get_entry`, `fetch_entries_to`, `compact_to`, `purge_expired_files`, `raft_groups`, `is_empty`, `file_span`, `get_used_size`, `path`, `consistency_check_with_file_system`, `unsafe_repair_with_file_system`, `dump_with_file_system`, `read_entry_from_file`, and `read_entry_bytes_from_file`.

## Control Flow
Open sanitizes config, adds a purge hook listener, scans log files, recovers append and rewrite queues through `FilePipeLogBuilder`, merges append context into rewrite context, builds memtables/stats, constructs a purge manager, and starts a background metrics flusher. `write` finalizes a `LogBatch`, enters the write barrier so a leader appends grouped writers, optionally syncs the append queue, handles one `TryAgain` retry for no-space spill behavior, applies written commands to memtables, notifies listeners, and records metrics/perf context. Reads consult memtables for entry indexes or key-values and fetch entry bytes from pipe-log blocks using a thread-local one-block cache. Tooling APIs recover with special replay machines or readers.

## State And Persistence Behavior
Durable state lives in append and rewrite log queues. Memtables and stats are reconstructed from replay on open. Compaction writes `Command::Compact`; clean commands remove raft groups; purge rewrites live entries and deletes or recycles obsolete files. `sync` fdatasyncs the append queue. `Drop` stops and joins the metrics thread.

## Dependencies And Integration Points
Integrates with `Config`, `FileSystem`, `FilePipeLog`, `PipeLog`, `LogBatch`, memtables, `PurgeManager`, `EventListener`, write barrier grouping, protobuf decoding, metrics, perf context, consistency checker, dump readers, and optional Rhai repair filters.

## Risks And Edge Cases
The non-empty write path panics on sync error while `Engine::sync` returns an error. Empty synced writes must still call `sync`, which is explicitly handled. Fetching entries must tolerate indexes becoming stale during concurrent rewrite by rereading memtable under lock. Recovery mode determines corruption tolerance. Unsafe repair can destroy data if scripts filter incorrectly. Metrics thread shutdown unwraps send/join results.

## Test Signals
In-file tests cover empty engines, get/fetch/read after recovery, key-value scan/delete, clean and compact interactions, purge triggers, rewrite/recover, empty protobuf messages, empty synced batches, dirty recovery, large rewrite batches, format-version/recycle compatibility, dump and repair tools, tail corruption, wrong filesystem detection, managed deletion/reuse metadata, perf context, atomic rewrite groups, concurrent fetch with rewrite, internal-key filtering, and multi-directory spill behavior.
