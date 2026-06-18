<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleFileCacheWithSASConfig.yaml -->
# sources/user-network-fs/blobfuse2/sampleFileCacheWithSASConfig.yaml

## Purpose
Example Blobfuse2 file-cache configuration using SAS-token authentication instead of account key.

## Important APIs, Types, and Functions
Sections mirror `sampleFileCacheConfig.yaml`, but `azstorage` uses `sas: <SAS_TOKEN>` and `mode: sas`. Pipeline remains `libfuse`, `file_cache`, `attr_cache`, `azstorage`.

## Control Flow and State
At runtime this config mounts a SAS-authenticated block blob container and caches file contents on local disk under `file_cache.path`.

## Dependencies and Integration Points
Requires a valid SAS token, account name, container name, and local cache path. Consumed by Blobfuse2 config parsing and Azure storage client initialization.

## Risks and Edge Cases
SAS tokens are secrets and often contain special characters; deployment tooling must preserve them correctly. Token expiry or insufficient permissions will fail mount or operations. `log_debug` may expose operational details.

## Test Signals
Documents intended SAS file-cache wiring. Real validation requires replacing placeholders and mounting against Azure Storage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleFileCacheWithSASConfig.yaml -->
