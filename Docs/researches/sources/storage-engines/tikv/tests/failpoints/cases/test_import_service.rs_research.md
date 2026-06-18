# sources/storage-engines/tikv/tests/failpoints/cases/test_import_service.rs

Purpose: exercises SST import service concurrency, resource limits, ingestion idempotency/conflicts, encryption cleanup, v2 cleanup, bucket/split metadata, applied-index flushing, and duplicate detection stream behavior.

Important APIs and functions: uses import grpc client methods `download`, `ingest`, `ingest_async`, `switch_mode`, `duplicate_detect`, helpers from `test_sst_importer` and integrations import util, and `sst_file_count`. Tests include concurrent download success/failure, blocking SST writer, download under disk/memory pressure, reentrant ingest, key-manager delete failure, ingest conflicts, stale-epoch cleanup, applied-SST cleanup, bucket update after ingest, flushed applied index after ingest, and duplicate detect client-stop handling.

Control flow: tests generate SST files in temp dirs, upload or download them through import service, inject failpoints such as `create_local_storage_yield`, `on_open_sst_writer`, `mock_memory_usage`, `key_manager_fails_before_delete_file`, `before_sst_service_ingest_check_file_exist`, `on_cleanup_import_sst_schedule`, `on_flush_completed`, `on_update_region_keys`, `on_apply_ingest`, and `failed_to_async_snapshot`, then ingest or stream and assert data or error messages.

State and persistence: import-sst files, encrypted file keys, region epoch metadata, applied-index flush state, bucket metadata, and duplicate-detect SST contents are persisted or tracked. Several tests restart clusters to validate cleanup durability.

Dependencies and integration: integrates `kvproto::import_sstpb`, TiKV config, local external storage, grpc, disk usage status, raftstore simulator, TDE import setup, and raw KV client writes.

Risks and test signals: high concurrency and fixed timeouts can be flaky under slow IO. Signals include no deadlocks on duplicate downloads, correct resource errors, idempotent ingest, no stale file resurrection, and robust streaming cancellation.
