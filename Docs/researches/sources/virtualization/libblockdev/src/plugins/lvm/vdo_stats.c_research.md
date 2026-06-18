# File Research: sources/virtualization/libblockdev/src/plugins/lvm/vdo_stats.c

## Role
Implements VDO stats retrieval and normalization for the LVM plugin. It talks directly to device mapper, requests the VDO target `stats` message, parses the YAML response, and returns a GLib hash table of string key/value statistics.

## Main Flow
- `vdo_get_stats_full(name, error)` creates a `DM_DEVICE_TARGET_MSG` task, sets the DM device name, sends the `stats` target message, obtains the response, and parses it with libyaml.
- The parser scans YAML tokens and records scalar key/value pairs into a `GHashTable`.
- Flow mappings are flattened by using the previous key as a prefix and uppercasing the first character of nested keys to preserve camelCase-style names.
- On success, computed compatibility statistics are added before returning the hash table.

## Parsing Helpers
- `get_stat_val64()` reads an integer stat from the hash table and rejects missing or partially parsed values.
- `get_stat_val64_default()` returns a default value when parsing fails.
- `get_stat_val_double()` reads floating-point stats and rejects partial parses.

## Computed Stats
- `add_write_ampl_r_stats()` derives `writeAmplificationRatio` from `biosMetaWrite`, `biosOutWrite`, and `biosInWrite`.
- `add_block_stats()` derives `oneKBlocks`, `oneKBlocksUsed`, `oneKBlocksAvailable`, `usedPercent`, `savings`, and non-negative `savingPercent` from block counts and block size.
- `add_journal_stats()` derives batching/writing counters for journal entries and blocks.
- `add_computed_stats()` also adds `fiveTwelveByteEmulation` based on whether `logicalBlockSize` is `512`.

## Error Handling
- Device-mapper task creation, name setup, message setup, task execution, response retrieval, and YAML parser initialization all produce `BD_LVM_ERROR_DM_ERROR` on failure.
- The parser assumes YAML scanning succeeds; it does not explicitly check `yaml_parser_scan()` failure state in the token loop.

## Filesystem/Storage Relevance
The file converts low-level VDO target telemetry into libblockdev-accessible statistics. These stats matter for deduplicated/compressed block volumes that may host filesystems, especially capacity reporting, savings reporting, and write-amplification monitoring.
