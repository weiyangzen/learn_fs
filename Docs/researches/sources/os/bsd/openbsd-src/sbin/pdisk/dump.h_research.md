# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/dump.h

Purpose: Public prototypes for `pdisk` partition-map dump routines.

Declared API:
- `dump_partition_map(struct partition_map *)`
- `full_dump_partition_entry(struct partition_map *, int)`
- `full_dump_block_zero(struct partition_map *)`
- `show_data_structures(struct partition_map *)`

Integration:
- Included by command/UI code that needs human-readable partition map output.
- Relies on `struct partition_map` being declared before use.
