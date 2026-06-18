<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleFileCacheConfig.yaml -->
# sources/user-network-fs/blobfuse2/sampleFileCacheConfig.yaml

## Purpose
Example Blobfuse2 configuration for a file-cache pipeline using account-key authentication.

## Important APIs, Types, and Functions
Defines `logging`, `components`, `libfuse`, `file_cache`, `attr_cache`, and `azstorage`. Components are `libfuse`, `file_cache`, `attr_cache`, `azstorage`. File cache requires a local `path`, uses 120 second timeout, and caps size at 4096MiB.

## Control Flow and State
When used at mount time, it assembles a file-cache pipeline and persists cached file data under the configured cache path. Attribute cache timeout is set to 7200 seconds.

## Dependencies and Integration Points
Consumed by Blobfuse2 config parsing and Azure storage auth. Requires replacing cache path and account/container/key placeholders.

## Risks and Edge Cases
The local cache path must have enough disk space and appropriate permissions. `log_debug` can generate high log volume. Real account keys must not be stored in sample-derived committed configs.

## Test Signals
The file documents expected key-auth file-cache setup. Validating it requires a real mount or config parser smoke test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleFileCacheConfig.yaml -->
