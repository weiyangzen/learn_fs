# File Research: sources/virtualization/nbdkit/plugins/partitioning/virtual-disk.c

## Purpose
Constructs the partitioning plugin’s virtual region layout, allocating synthetic partition table storage and arranging file/metadata/zero regions.

## Main Entry Points
- `create_virtual_disk_layout()` allocates MBR/GPT metadata buffers, appends the primary table region, appends partition file regions with alignment and padding, appends EBR regions for MBR logical partitions, appends secondary GPT metadata, logs regions when debugging, validates final alignment, and calls `create_partition_table()`.
- `create_partition_table()` dispatches to MBR or GPT layout creation.

## Dependencies
Uses common regions APIs, alignment helpers, virtual-disk globals, and nbdkit logging.

## Risks and Notes
Partial allocation failures can leave earlier allocations for unload cleanup, but the function returns early without local rollback. The region layout must be constructed before partition-table bytes are filled because MBR/GPT entries depend on final virtual offsets.
