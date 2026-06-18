# File Research: sources/os/linux/linux/block/partitions/sgi.c

## Summary
Recognizes SGI disklabels and emits up to 16 partition entries.

## Main Responsibilities
- Validates the SGI magic.
- Computes and verifies the disklabel checksum.
- Emits nonempty partitions.
- Marks SGI entries with Linux RAID type for md autodetect.

## Key API
- `sgi_partition()`.

## Important Behavior
The checksum is a 32-bit sum over the label interpreted as big-endian words and must equal zero. Partition start and block count are big-endian logical block values used directly as Linux sectors.

## Risks
The code increments output slots across all 16 SGI entries, including empty ones. It does not explicitly cap against `state->limit`, relying on historical assumptions about minor counts and sparse labels.
