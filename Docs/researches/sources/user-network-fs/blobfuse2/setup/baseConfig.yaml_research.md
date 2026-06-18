<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/baseConfig.yaml -->
# sources/user-network-fs/blobfuse2/setup/baseConfig.yaml

## Purpose
Shorter reference template for common Blobfuse2 configuration sections.

## Important APIs, Types, and Functions
Includes `logging`, `components`, `xload`, `block_cache`, `file_cache`, and `azstorage`. The component order is `libfuse`, `xload`, `block_cache`, `file_cache`, `attr_cache`, `azstorage`.

## Control Flow and State
Like the advanced config, this is an annotated template rather than a directly usable YAML file. Realized values influence cache paths, cache sizes, auth mode, endpoint, account, and container.

## Dependencies and Integration Points
Used by sample configs and setup docs as the baseline option reference. Aligns with Blobfuse2 config parsing.

## Risks and Edge Cases
Inline explanatory placeholders make the file invalid as-is. It lists mutually exclusive cache components together to document choices, so users must remove unused components. Secret fields must be handled carefully.

## Test Signals
Documentation consistency and successful user-derived configs are the primary signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/baseConfig.yaml -->
