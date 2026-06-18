# File Research: sources/os/linux/linux/block/partitions/karma.c

## Summary
Recognizes the Rio Karma media-player partition label.

## Main Responsibilities
- Reads sector 0.
- Validates the Karma disklabel magic `0xAB56`.
- Exposes up to two partitions whose filesystem type byte is `0x4d`.

## Key API
- `karma_partition()`.

## Important Behavior
The on-disk label is defined locally as a packed structure. Partition offsets and sizes are little-endian 32-bit sector counts. Empty partitions are skipped but slot numbering still advances.

## Risks
The parser is intentionally narrow and accepts only two entries with a specific type byte. Any read failure returns `-1`, allowing the partition core to treat it as an I/O failure candidate.
