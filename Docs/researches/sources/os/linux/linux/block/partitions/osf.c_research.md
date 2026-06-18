# File Research: sources/os/linux/linux/block/partitions/osf.c

## Summary
Recognizes OSF/1-style disklabels stored in sector 0 at offset 64.

## Main Responsibilities
- Reads the disklabel from sector 0.
- Validates both disklabel magic fields.
- Bounds-checks the partition count against 18.
- Emits nonempty partitions.

## Key API
- `osf_partition()`.

## Important Behavior
Partition offsets and sizes are little-endian sector counts. Slot numbering follows disklabel order and advances even over empty entries.

## Risks
No checksum validation is performed despite the structure containing a checksum field. The parser trusts the bounded partition count after magic validation.
