# File Research: sources/os/linux/linux/block/partitions/amiga.c

Implements Amiga Rigid Disk Block partition table parsing.

Key responsibilities:
- Scans early disk blocks up to `RDB_ALLOCATION_LIMIT` for an `IDNAME_RIGIDDISK` block.
- Validates RDB checksums, with a compatibility retry for Windows-damaged bytes.
- Follows the RDB partition list and validates each `PartitionBlock`.
- Converts Amiga block/cylinder geometry into 512-byte Linux sectors.
- Performs overflow checks before calculating start and size.
- Emits up to 16 partition entries.

Important functions:
- `checksum_block()` computes the big-endian summed-long checksum.
- `amiga_partition()` is the parser entry point.

Safety details:
- Uses `check_mul_overflow()` and `check_add_overflow()` for multi-field geometry math.
- Warns when a partition exceeds 32-bit AmigaDOS limits.
- Skips invalid partition blocks or partitions with zero size.
- Emits DOS type and environment info into parser output for mounting diagnostics.

Research relevance:
- This file is a robust legacy parser example with explicit overflow hardening around old-disk geometry fields.
