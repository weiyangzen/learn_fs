# File Research: sources/os/linux/linux/block/partitions/check.h

Defines the shared interface for block partition parsers.

Key contents:
- `struct parsed_partitions` stores the target disk, partition name prefix, output partition array, limit, beyond-EOD flag, and sequence buffer for diagnostic output.
- `Sector` wraps a folio reference returned by `read_part_sector()`.
- `read_part_sector()` reads one sector for parser use.
- `put_dev_sector()` drops the folio reference.
- `put_partition()` records a partition start/size and appends its name to parser output.
- Declares parser entry points for all supported partition formats.

Research relevance:
- This header is the minimal parser ABI: parsers read sectors, call `put_partition()`, and return probe status.
- It also centralizes parser result storage and diagnostic string construction.
