# sources/storage-engines/tikv/components/compact-log-backup/src/test_util.rs

Purpose: supplies compact-log-backup test infrastructure for generating synthetic log files, temporary storage, expected compaction output, and result verification.

Important APIs and types: `Kv`, `LogFileBuilder`, `CompactInMem`, `RecordSorted`, `KvGen`, `KeySeed`, `TmpStorage`, `verify_the_same`, `sow`, `gen_step`, `gen_adjacent_with_ts`, `gen_min_max`, `build_many_log_files`, `save_many_log_files`, and `save_many_logs_files`.

Control flow: `LogFileBuilder` encodes stream-event key/value records into a Zstd buffer while tracking timestamps, key bounds, CRC64, entry count, and SHA256. Flush helpers combine builders into BR `Metadata` and physical log files. `TmpStorage` creates local external storage, builds backup flushes, runs subcompactions, loads migrations/subcompaction batches, and verifies generated SST files against an in-memory sorted/deduped expectation.

State and persistence: writes temporary local-storage objects and leaks the temp directory only on test panic to aid debugging. `CompactInMem` stores expected compacted KV state in a `BTreeMap`.

Dependencies and integration: used heavily by source, storage, compaction, and execution tests. Depends on Rocks SST readers/writers, external storage, BR protobufs, stream-event encoding, table row-key encoding, transaction keys, and SHA256 utilities.

Risks: helper assumptions mirror current production output, such as one SST per result and specific SST filename parts; changes in production naming or splitting require test utility updates. `CompactInMem::must_iter` panics if concurrent writes remain.

Test signals: this file is test-only and enables most higher-level behavioral validation across compact-log-backup.
