# File Research: sources/os/linux/linux/block/partitions/sun.c

## Summary
Recognizes Sun disklabels and emits Sun partition entries.

## Main Responsibilities
- Validates Sun label magic and XOR checksum.
- Optionally validates and uses the embedded Sun VTOC.
- Converts cylinder-based starts to sectors.
- Marks Linux RAID and whole-disk entries from VTOC IDs.

## Key API
- `sun_partition()`.

## Important Behavior
Partition start sectors are computed as `start_cylinder * ntracks * nsect`; sizes are already sector counts. If VTOC sanity/version/count are valid, VTOC IDs control RAID and whole-disk flags. Empty legacy VTOC metadata is also treated as usable for old Linux-Sun compatibility.

## Risks
Geometry fields in the label drive start conversion. Corrupt or unexpected VTOC metadata can change whether special flags are applied.
