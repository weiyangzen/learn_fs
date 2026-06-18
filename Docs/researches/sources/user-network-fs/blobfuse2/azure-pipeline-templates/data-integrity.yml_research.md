# sources/user-network-fs/blobfuse2/azure-pipeline-templates/data-integrity.yml

## Purpose
This template validates data consistency for file cache, block cache, read-only, direct-IO, disk block-cache path, and legacy stream configuration paths.

## Important APIs, Types, and Functions
It composes `data.yml` for data generation/copy/checks and `mount.yml` for mount lifecycle. It calls `blobfuse2 gen-test-config` with `azure_key.yaml`, `azure_key_bc.yaml`, and `azure_stream.yaml`, then mounts with options such as `--file-cache-timeout=3200`, `-o direct_io`, `-o ro`, and block-cache path/block-size flags.

## Control Flow
It first generates random local test files. For `file_cache`, it creates a file-cache config, mounts normally and with direct IO, copying and verifying data each time. For `block_cache`, it creates a block-cache config, tests normal, direct IO, read-only verify, direct IO with explicit disk block-cache path and block size, repeats verification against cached disk blocks, and finally tests backward-compatible stream config redirecting to block cache.

## State and Persistence Behavior
It creates local data under `$(ROOT_DIR)/data_files`, writes config files, uses `$(MOUNT_DIR)` and `$(TEMP_DIR)`, writes/reads data in Azure containers, and publishes/tails `blobfuse2-logs.txt` on failure.

## Dependencies and Integration Points
It depends on `data.yml`, `mount.yml`, generated containers, account credentials, and repository config templates. It is used by nightly FileCacheValidation and BlockCacheValidation stages.

## Risks and Edge Cases
The template prints configs. A failed cleanup can cause later verification to read stale data. The read-only block-cache case assumes data from previous writes remains available. Stream compatibility is tested under the block-cache branch only.

## Test Signals
Signals are successful MD5 comparisons from `data.yml`, clean mounts across all options, and failure artifacts/log tails when a mode corrupts or hides data.
