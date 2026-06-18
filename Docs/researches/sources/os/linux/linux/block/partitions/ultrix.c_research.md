# File Research: sources/os/linux/linux/block/partitions/ultrix.c

## Summary
Recognizes Ultrix partition tables located near the 16 KiB boundary.

## Main Responsibilities
- Reads the sector containing the trailing Ultrix disklabel.
- Validates magic `0x032957` and valid flag `1`.
- Emits up to eight nonempty partitions.

## Key API
- `ultrix_partition()`.

## Important Behavior
The label is expected at the end of the 16 KiB area, so the parser reads sector `(16384 - sizeof(label)) / 512` and offsets within that sector.

## Risks
The on-disk fields are read in native layout rather than explicit endian helpers, matching the historical target format but making the recognizer architecture-sensitive.
