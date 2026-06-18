# sources/storage-engines/wiredtiger/src/conn/conn_layered_page_log.c

## Purpose
This file implements the connection-side disaggregated-storage page-log helpers for metadata, checkpoint metadata, and key-provider material. It is the bridge between WiredTiger checkpoint/turtle metadata and the `WT_PAGE_LOG` extension interface used by disaggregated storage and layered tables. It also owns the serialization, validation, and in-memory queueing rules for encryption key material that must be persisted into the page log.

## Important APIs, Types, and Functions
Important exported entry points include `__wti_layered_get_disagg_checkpoint`, `__wti_disagg_load_crypt_key`, `__wti_disagg_parse_crypt_meta`, `__wti_disagg_pending_crypt_key_clear`, `__wti_disagg_set_crypt_key`, `__wt_disagg_put_crypt_helper`, `__wti_disagg_fetch_shared_meta`, `__wt_disagg_put_checkpoint_meta`, and `__wt_disagg_parse_meta`. Key local helpers are `__disagg_get_page`, `__disagg_put_page`, `__disagg_validate_crypt`, `__disagg_set_crypt_header`, `__disagg_select_pending_crypt_key`, `__disagg_prune_pending_crypt_keys`, `__disagg_get_meta`, `__disagg_put_meta`, `__disagg_parse_legacy_meta`, `__disagg_parse_meta`, and `__disagg_parse_version_and_check`.

The main data structures are `WT_DISAGGREGATED_STORAGE`, `WT_PAGE_LOG_HANDLE`, `WT_PAGE_LOG_GET_ARGS`, `WT_PAGE_LOG_PUT_ARGS`, `WT_DISAGG_METADATA`, `WT_DISAGG_CHECKPOINT_META`, `WT_CRYPT_KEYS`, `WT_CRYPT_HEADER`, and `WT_DISAGG_PENDING_CRYPT_KEY`.

## Control Flow and Behavior
Page-log reads and writes flow through `__disagg_get_page` and `__disagg_put_page`, both of which require the connection checkpoint lock. Reads retry up to 100 times to tolerate page materialization delay and fail with `EIO` after repeated misses. Writes chain the previous LSN via `backlink_lsn`, update the per-page last-LSN array, and optionally return the new LSN.

Encryption-key load starts from checkpoint metadata: `__wti_disagg_load_crypt_key` parses page ID/LSN metadata, reads the key-provider page, validates checksum/header/version/signature, points `WT_CRYPT_KEYS` at the payload, calls `key_provider->load_key`, and prunes queued pushed keys up to the loaded timestamp. Key persistence happens in `__wt_disagg_put_crypt_helper`, which either selects a queued push-mode key at or before the checkpoint timestamp or asks pull-mode providers via `get_key`; it then prepends a `WT_CRYPT_HEADER`, writes the key page, and calls `on_key_update` with either LSN or error.

Checkpoint metadata persistence is handled by `__wt_disagg_put_checkpoint_meta`: it captures checkpoint root, checkpoint timestamp, oldest timestamp, schema epoch, largest file ID, optional key-provider metadata, and checksum, writes the metadata page, then atomically updates in-memory last-checkpoint fields. Metadata parsing supports both the legacy newline format and current config format, with version/compatible-version validation before parsing current fields.

## State and Persistence
Persistent state is stored in page-log pages for checkpoint metadata and key-provider payloads. In-memory state includes `last_metadata_page_lsn`, `last_key_provider_page_lsn`, `last_checkpoint_meta_lsn`, `last_checkpoint_timestamp`, `last_checkpoint_oldest_timestamp`, `last_checkpoint_schema_epoch`, `last_checkpoint_meta_checksum`, `last_checkpoint_root`, `num_meta_put`, and the pending key tail queue. Durable metadata includes `checkpoint`, `timestamp`, `oldest_timestamp`, `schema_epoch`, `largest_file_id`, optional `key_provider`, and checksum tracked separately in checkpoint metadata.

## Dependencies and Integration Points
The file depends on WiredTiger config parsing, scratch buffers, checksums, metadata checkpoint readers, timestamp parsing/formatting, checkpoint/schema locks, key-provider callbacks, disaggregated connection configuration, and the page-log extension API. It is called from checkpoint, recovery/reconfigure, disaggregated metadata fetch, key-provider rotation, and layered/disaggregated tests.

## Risks
Important risks are checkpoint-lock misuse, corrupt or incompatible metadata silently accepted, bad byte swapping or checksum handling for crypt headers, stale LSN arrays producing broken backlink chains, push-mode queued keys being selected after lock release, and failures after the metadata page write but before in-memory bookkeeping. The code intentionally treats the page-log metadata write as the last fallible operation in `__wt_disagg_put_checkpoint_meta`.

## Test Signals
Useful signals include unit-test hooks under `HAVE_UNITTEST` for crypt header validation and metadata version parsing, disaggregated storage tests that fetch complete checkpoints, key-provider crash-trigger tests around before/during/after rotation, metadata corruption checksum tests, and compatibility tests for legacy/current checkpoint metadata.
