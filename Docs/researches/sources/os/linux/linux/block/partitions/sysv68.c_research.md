# File Research: sources/os/linux/linux/block/partitions/sysv68.c

## Summary
Recognizes Motorola/System V/68 disk slice tables.

## Main Responsibilities
- Validates the `MOTOROLA` volume identifier in sector 0.
- Reads the slice table block indicated by the config block.
- Emits all nonempty slices except the final whole-disk slice.

## Key API
- `sysv68_partition()`.

## Important Behavior
The first disk sector is interpreted as two 256-byte structures: volume id and disk config. Slice count and slice table block are big-endian. The last slice is intentionally skipped because it represents the whole disk.

## Risks
The parser trusts the slice count and slice-table block after the volume identifier check, with no explicit range check beyond read failure and `state->limit`.
