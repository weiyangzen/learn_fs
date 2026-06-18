# sources/storage-engines/tikv/tests/integrations/server/debugger.rs

Purpose: tests debugger compaction and flashback-to-version behavior, especially for raftstore v2 tablet-backed storage.

Important APIs and functions: `gen_mvcc_put_kv`, `gen_delete_k`, `test_compact`, `test_flashback_to_version`, `test_flashback_to_version_without_prepare`, `test_flashback_to_version_with_mismatch_ts`, and `flashback_to_version`.

Control flow: compaction creates three split regions, writes and flushes MVCC write-CF records, deletes and flushes them, captures tablet approximate sizes, runs `DebuggerImplV2::compact` over several ranges, and verifies only expected tablet sizes drop. Flashback tests write many versions, enumerate regions through debug RPCs, and issue prepare/finish flashback requests including missing-prepare and mismatched-ts error cases.

State and persistence: manipulates persisted tablet RocksDB state, write CF records, deleted keys, and debug flashback state. Flashback changes MVCC history and is checked with KV reads or strict gRPC errors.

Dependencies and integration: `DebuggerImplV2`, `ConfigController`, tablet cache iteration, RocksDB range sizes, debugpb/debug gRPC, MVCC write encoding, and raftstore cluster helpers.

Risks: approximate-size assertions depend on RocksDB flush/compaction behavior; flashback errors depend on exact state-machine messages; data-key boundaries must be encoded correctly.

Test signals: validates debugger compaction range targeting and flashback prepare/finish state enforcement.
