# sources/storage-engines/tikv/tests/integrations/backup/mod.rs

## sources/storage-engines/tikv/tests/integrations/backup/mod.rs

Purpose: integration coverage for TiKV backup pushdown, local external storage output, SST import restoration, raw KV API-version conversion, raw backup metadata, failure paths, commit timestamp safety, and backup during flashback.

Important APIs and helpers: `TestSuite`, `backup`, `backup_raw`, `storage_raw_checksum`, `make_local_backend`, `create_storage`, `SstImporter::create`, raft `IngestSst` commands, `SstMeta`, `calc_crc32_bytes`, `checksum_crc64_xor`, and `assert_same_files`. `assert_same_files` normalizes timestamp-bearing file names, random cipher IVs, and RocksDB session-dependent SHA fields before comparing backup output.

Control flow: tests create multi-node suites, write MVCC or raw KV data, run backup streams with `block_on(rx.collect())`, delete or restore data through direct CF deletion and importer ingestion, then run a second backup to compare logical file metadata. Raw KV tests back up from V1/V1ttl/V2 to target API versions and verify restored reads plus metadata counts/checksums. Error and edge tests cover read-only storage, async-commit/1PC min commit timestamps after backup, and backup while a region is in prepared flashback state.

State and persistence: the tests persist generated SSTs into temporary local storage, copy them into each simulated store importer, and ingest via raft command so restored RocksDB state is observable through subsequent backup or raw get calls. They also mutate cluster CF contents directly and use flashback admin commands.

Dependencies and integration points: `test_backup`, `kvproto`, `external_storage`, `engine_traits`, raft command protobufs, transaction timestamps, and TiKV coprocessor checksum. Risks include nondeterministic file metadata, file permissions skipped in docker-root runs, and API-version key encoding differences. Test signals are end-to-end backup/import equality, raw checksum parity, expected storage error responses, and absence of flashback backup errors.
