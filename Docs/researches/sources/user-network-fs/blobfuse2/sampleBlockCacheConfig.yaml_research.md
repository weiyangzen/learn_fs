<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleBlockCacheConfig.yaml -->
# sources/user-network-fs/blobfuse2/sampleBlockCacheConfig.yaml

## Purpose
Example Blobfuse2 configuration for a block-cache pipeline using account-key authentication.

## Important APIs, Types, and Functions
Key sections are `logging`, `components`, `libfuse`, `block_cache`, `attr_cache`, and `azstorage`. Components are ordered as `libfuse`, `block_cache`, `attr_cache`, `azstorage`. Block cache is configured with 32MiB blocks, 4096MiB memory, prefetch 80, and parallelism 128.

## Control Flow and State
This declarative YAML controls runtime pipeline assembly and cache sizing when passed to Blobfuse2. It does not persist state itself; the block cache may maintain memory/disk cache depending on full runtime defaults and extra config.

## Dependencies and Integration Points
Consumed by Blobfuse2 config parsing. Placeholders `<ACCOUNT_NAME>`, `<ACCOUNT_KEY>`, and `<CONTAINER_NAME>` must be replaced. It refers readers to `setup/baseConfig.yaml` for the full config surface.

## Risks and Edge Cases
The sample uses `log_debug`, which is verbose for production. Large prefetch and parallelism values can overconsume memory/network resources. Account-key placeholders must not be committed with real secrets.

## Test Signals
Serves as documentation/config smoke input rather than an automated test. It signals the intended component ordering for block-cache scenarios.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleBlockCacheConfig.yaml -->
