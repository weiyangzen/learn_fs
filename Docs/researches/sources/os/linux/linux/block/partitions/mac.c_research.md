# File Research: sources/os/linux/linux/block/partitions/mac.c

## Summary
Recognizes Apple Partition Map disks and exports map entries as Linux partitions.

## Main Responsibilities
- Validates the driver descriptor in block 0.
- Reads the first Apple partition map entry.
- Uses the map count to iterate partition entries.
- Marks `Linux_RAID` entries for md autodetect.
- On PowerMac, records the most plausible boot/root partition.

## Key API
- `mac_partition()`.

## Important Behavior
The parser requires the driver descriptor magic and a power-of-two on-disk block size. Partition entries may be offset within a 512-byte sector when the Mac block size is not a multiple of 512, so the parser computes the byte offset carefully.

For each valid entry, start and length are converted from Mac blocks to 512-byte sectors. On `CONFIG_PPC_PMAC`, it trims strings and scores bootable PowerPC Unix/Linux partitions to call `note_bootable_part()`.

## Risks
The parser depends on valid `block_size` and `map_count` values from disk. Non-power-of-two block sizes are rejected because partition entries could straddle sectors in ways `read_part_sector()` cannot safely handle.
