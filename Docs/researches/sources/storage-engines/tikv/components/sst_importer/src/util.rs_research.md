# sources/storage-engines/tikv/components/sst_importer/src/util.rs

## Purpose
This utility file provides filesystem preparation helpers used before SST ingestion and a small external-storage URL helper. The ingestion helpers make retryable ingestion safe when RocksDB may move, mutate, or delete the input SST during external file ingestion.

## Important APIs, Types, And Functions
`prepare_sst_for_ingestion(path, clone, encryption_key_manager)` removes any stale clone and encryption metadata, then either hard-links or copies the source SST to a clone path. On Unix it reads the source link count: if there is only one link, RocksDB should not already own the file and a hard link is safe; otherwise it copies to avoid modifying an SST that may already have been ingested. It syncs the clone file and parent directory, then links encryption metadata from original to clone when a `DataKeyManager` is present.

`copy_sst_for_ingestion` is a stricter variant that always copies, removes read-only permission from the clone if necessary, syncs the parent directory, and updates encryption metadata. `url_for` converts `ExternalStorage::url()` to a string and makes URL lookup errors printable as `ErrUrl(...)`.

## Control Flow And State
The helpers are idempotent over an existing clone path: they remove both filesystem file and key-manager entry before recreating the clone. The branch in `prepare_sst_for_ingestion` is driven by filesystem metadata and is only link-count aware on Unix. `copy_sst_for_ingestion` has no hard-link branch and always produces a separately writable file.

## Persistence And Integration Points
This code is explicitly about durable filesystem state. It uses `file_system::{remove_file, hard_link, copy_and_sync, metadata, set_permissions}` and `File::sync_all` to make both clone file contents and containing-directory metadata durable. It integrates with encryption metadata by deleting stale clone keys and then calling `DataKeyManager::link_file`.

## Risks And Test Signals
The functions call `to_str().unwrap()` and assume ordinary UTF-8 filesystem paths. Parent directory lookup is also unwrapped. Incorrect link-count assumptions can corrupt ingested SSTs because RocksDB may mutate global sequence numbers, which is why multi-link files are copied. Tests exercise hard-link first ingestion, copy after ingestion, repeated preparation, Titan SSTs, plaintext and encrypted key-manager scenarios, and the always-copy helper.
