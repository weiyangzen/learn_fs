# sources/storage-engines/wiredtiger/src/tiered/tiered_config.c Research

## Purpose
This file parses and applies tiered-storage bucket configuration at connection and table scope. It builds or reuses `WT_BUCKET_STORAGE` instances, customizes storage-source file systems, enforces compatibility rules, and stores connection-level tiered options such as interval and local retention.

## Important APIs, Types, and Functions
- `__tiered_common_config` reads common options such as `tiered_storage.local_retention` into `WT_BUCKET_STORAGE::retain_secs`.
- `__wti_tiered_bucket_config` resolves `tiered_storage.name`, opens a named storage source, validates bucket and prefix requirements, reuses existing bucket storage by hash lookup, or creates and registers a new `WT_BUCKET_STORAGE`.
- `__wt_tiered_conn_config` configures `conn->bstorage`, rejects incompatible connection modes, sets `conn->tiered.interval`, updates tiered statistics, and initializes the special `bstorage_none` file-system mapping.

## Control Flow and State
Bucket configuration starts by opening the named storage source under `conn->ext.storage_lock`. If no storage source is named, the function rejects stray bucket settings and returns no bucket storage. If table-level tiering is requested without connection tiering, it returns `EINVAL`. A table cannot enable shared tiering unless the connection bucket storage is also shared. Existing bucket storage is found by hashing the bucket name and matching bucket plus prefix. New bucket storage duplicates auth token, bucket, prefix, cache directory, calls `ss_customize_file_system`, inserts into source queues and hash queues, marks it freeable, and applies common retention settings.

## State and Persistence Behavior
This module mutates connection in-memory state and extension-owned storage-source queues. It does not itself write metadata, but its result is embedded into tiered handles that later create object metadata and schedule flush/remove work. Retention seconds directly influence when local objects are removed after shared flush.

## Dependencies and Integration Points
The code integrates with the extension storage-source registry, named storage source lookup, CityHash bucket hashing, WiredTiger config parsing, connection flags, statistics, and tiered handle open paths. `__wti_tiered_bucket_config` is used by both connection configuration and per-table tiered open logic.

## Risks and Edge Cases
The function holds `storage_lock` while opening/customizing storage sources and manipulating queue/hash membership, so any storage-source callback that calls back into locked extension state could deadlock if contracts are violated. The error path frees only selected fields of `new`; auth/cache/file-system cleanup depends on storage-source ownership conventions and broader close cleanup. Reconfiguration only reapplies common options to existing connection storage and intentionally does not remove newly created bucket storage if a later connection config step fails.

## Test Signals
Tests should validate missing name plus bucket rejection, missing bucket/prefix rejection, table tiering without connection tiering rejection, shared mismatch rejection, reuse of identical bucket/prefix storage, distinct prefix producing distinct storage, retention reconfiguration, in-memory connection incompatibility, and storage-source customize failures restoring `conn->bstorage` in `__wt_tiered_conn_config`.
