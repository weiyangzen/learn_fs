# sources/storage-engines/tikv/components/engine_rocks/src/compact_listener.rs

Purpose: Converts RocksDB compaction completion callbacks into TiKV `RocksCompactedEvent` values with key ranges and per-region declined-byte estimates.

Important APIs and types: `RocksCompactionJobInfo` wraps raw RocksDB job info and implements `engine_traits::CompactionJobInfo`. `RocksCompactedEvent` implements `CompactedEvent`. `CompactedEventSender` abstracts event delivery. `CompactionListener` implements `rocksdb::EventListener`.

Control flow: On compaction completion, the listener ignores failed jobs and jobs rejected by an optional filter. It collects input/output filenames, decodes range properties from table properties, separates input and output properties, derives smallest/largest input keys, and sends a `RocksCompactedEvent`. Event methods expose key range, declined bytes, trivial-decline classification, output level label, CF, and `calc_ranges_declined_bytes`, which maps compaction range overlap to region IDs and computes old-new size deltas above a threshold.

State and persistence behavior: Listener state is an event sender plus optional filter. Events are in-memory observations; they do not persist state. Declined-byte calculations use decoded SST range properties captured from the compaction job.

Dependencies and integration: Integrates RocksDB event callbacks with TiKV range property decoding and split-check or scheduling logic that consumes compaction events. Uses `collections::hash_set_with_capacity`, `RangeProperties`, and `UserCollectedPropertiesDecoder`.

Risks: If any SST property decode fails, the entire event is dropped after a warning. If both input and output properties are empty, or key bounds are missing, no event is sent. File matching depends on string paths from RocksDB. Declined-byte estimates are approximate and threshold-filtered.

Test signals: No local unit tests in this file; behavior is indirectly exercised by compaction/event integration tests elsewhere. Compile-time trait implementation protects the wrapper surface.
