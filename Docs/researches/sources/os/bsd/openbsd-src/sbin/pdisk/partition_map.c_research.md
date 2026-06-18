# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/partition_map.c

Implements Apple Partition Map loading, validation, creation, mutation, and writing for `pdisk`.

Key responsibilities:
- Opens an existing partition map from block zero plus DPME entries.
- Validates block-zero signature, sector size, media size, partition-entry count, DPME signatures, and logical-block ranges.
- Maintains two linked-list orderings of entries: `disk_order` by partition-map entry number and `base_order` by physical block start.
- Creates a default map with block zero, an initial `Apple_Free` span, and an `Apple_partition_map` entry.
- Adds partitions by splitting an enclosing `Apple_Free` entry into before/target/after pieces.
- Deletes partitions by converting them back into free space and coalescing adjacent `Apple_Free` entries.
- Renumbers disk addresses and updates each entry’s `dpme_map_entries`.
- Resizes the partition map entry when adjacent free space and map-capacity constraints allow.
- Writes block zero and each DPME entry back to disk.
- Detects and optionally removes driver descriptor references from block zero when deleting a containing partition.

Important functions and data:
- `open_partition_map()` allocates and initializes a map, reads block zero, validates it, reads DPME entries, or prompts to create a default map.
- `read_partition_map()` reads every declared DPME entry and checks count consistency, logical ranges, overlap, disk-end extension, and unmapped physical-block gaps.
- `create_partition_map()` constructs a new in-memory Apple partition map.
- `add_partition_to_map()` splits free space and inserts the requested partition.
- `delete_partition_from_map()`, `delete_entry()`, and `combine_entry()` remove entries and merge free space.
- `create_entry()` initializes DPME fields, names, types, logical size, flags, and list membership.
- `dpme_init_flags()` assigns special flags for free, map, HFS, and general data partitions.
- `move_entry_in_map()` swaps two map positions except partition 1.
- `resize_map()` shrinks or expands the map entry around adjacent free space.
- `contains_driver()` and `remove_driver()` consult and update the block-zero driver descriptor map.

Notable behavior:
- Media size is capped to `UINT32_MAX` in `open_partition_map()`, matching 32-bit Apple partition-map fields.
- The partition-map entry itself and free-space entries cannot be deleted through normal deletion.
- New OpenBSD/data partitions get valid, allocated, readable, and writable flags; `Apple_HFS` receives the legacy HFS flag value.
- Free entries have no logical blocks, while non-free entries default logical blocks to the full physical partition size.
- `add_partition_to_map()` rejects allocations outside an existing free partition and rejects changes that would exceed map capacity.
- `resize_map()` temporarily clears the map entry type before routing through deletion logic, then recreates the map entry at block 1.

Dependencies:
- Uses structures and constants from `partition_map.h`.
- Uses disk I/O helpers from `io.h`.
- Uses `read_block0`, `read_dpme`, `write_block0`, and `write_dpme`.
- Uses OpenBSD `sys/queue.h` list macros and standard allocation/diagnostic helpers.

Research notes:
- This file is the stateful partition-map engine behind `pdisk.c`.
- The dual-order list model is central: disk order controls DPME write positions, while base order controls allocation, overlap checks, and free-space coalescing.
