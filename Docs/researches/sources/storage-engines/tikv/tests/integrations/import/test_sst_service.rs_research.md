# sources/storage-engines/tikv/tests/integrations/import/test_sst_service.rs

Purpose: exercises TiKV ImportSST gRPC service behavior end to end against one-node server clusters and raftstore-v2 clusters. It covers raw upload, WriteSST-generated SSTs, ingest/multi-ingest, download from external storage, mode switching, duplicate detection, suspend controls, TDE, cleanup, admission control, and force partition compaction.

Important APIs and functions: `assert_to_string_contains!` normalizes error assertions. `run_test_write_sst` builds txn key/value batches with `send_write_sst`, ingests returned metas with `must_ingest_sst`, and validates committed transactional KVs. `switch_mode` wraps `SwitchModeRequest`. Tests drive `ImportSstClient` methods including `upload`, `write`, `ingest`, `multi_ingest`, `download`, `switch_mode`, `duplicate_detect`, `suspend_import_rpc`, and `add_force_partition_range`. Helpers from `test_sst_importer` generate SST metadata/data and validate ingested ranges.

Control flow: most tests create a cluster/client through `super::util`, create or stream SST data, set region id/epoch from the current context, call the ImportSST RPC, and then validate either the service error or persisted data through `TikvClient`. Split/merge tests mutate PD region metadata and wait for cleanup. Concurrent ingest spawns threads sharing an import client to assert admission-control limits. Flash import mode tests split regions, change mode by key range, then compare ingest acceptance in import vs normal mode.

State and persistence: tests intentionally persist SST files under import directories and RocksDB DB paths, verify duplicate UUID/file detection, check that uploaded files disappear after split/merge or nonexistent-region cleanup, and confirm compaction can repartition SST files on disk. TDE tests use an encrypted security config. Resource-full paths manipulate global disk status and failpoints for memory usage/limit.

Dependencies and integration points: depends on `kvproto::import_sstpb`, TiKV config, `ImportSstClient`, `TikvClient`, PD client region APIs, failpoints, RocksDB ingest behavior, external local storage backends, disk-status hooks, and raftstore split/merge operations.

Risks: timing-sensitive cleanup and region bucket polling can be flaky under slow CI. Some error checks match string fragments. Global disk-status and failpoint state must be reset or later tests can be contaminated. `test_cleanup_sst_v2` appears to set `Range.start` twice where an end bound may have been intended, making that subcase worth reviewing.

Test signals: successful data reads through `check_ingested_kvs`, `check_ingested_txn_kvs`, CF-specific checks, import error variants (`DiskSpaceNotEnough`, `server_is_busy`, `region_not_found`), duplicate-detect pair counts, on-disk SST counts, and cleanup by failed re-upload checks.
