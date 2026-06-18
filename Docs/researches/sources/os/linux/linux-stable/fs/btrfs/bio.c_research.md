# File Research: sources/os/linux/linux-stable/fs/btrfs/bio.c

## Summary
Implements the Btrfs bio submission and completion layer: logical-to-physical mapping, bio splitting, mirrored/parity submission, checksum preparation and verification, endio workqueue handoff, read repair, and repair writes.

## Main Responsibilities
- Allocates and initializes `btrfs_bio` objects.
- Splits bios at mapping, segment, or zone-append boundaries.
- Maps logical ranges to devices and stripes.
- Submits single-mirror, mirrored, and RAID56 bios.
- Computes write checksums synchronously or through Btrfs workers.
- Looks up and verifies data read checksums.
- Performs read repair by trying alternate mirrors and writing repaired sectors.
- Tracks device I/O errors and per-device stats.
- Initializes and tears down bio sets and failed-bio mempool.

## Important Behavior
`btrfs_submit_bbio()` loops through chunks until the whole logical bio is mapped. `btrfs_submit_chunk()` calls `btrfs_map_block()`, saves original logical addresses for data writes, handles zone append limits, splits partial mappings, preloads checksums for data reads, and computes or schedules checksums for data writes.

Read completion for data bios runs in task context. `btrfs_check_read_bio()` verifies checksums sector by sector and starts repair reads for bad sectors. Repair reads try alternate mirrors; successful repair data is written back to earlier failed mirrors through `btrfs_repair_io_failure()`.

Mirrored writes clone bios for all but the last mirror. Completion tolerates errors up to `bioc->max_errors`; only excess errors propagate upward. RAID56 uses the RAID56 parity layer and reports completion from workqueue context.

Zone append support rewrites device bio sectors to zone starts and records physical positions after successful completion. NODATASUM zoned writes may allocate dummy checksums where the ordered path expects them.

## Risks
The original `btrfs_bio` tracks split pending I/Os and first error status; clone completion must decrement and free in the right order. Checksum ownership differs between reads, normal writes, relocation roots, NODATASUM writes, remap writes, and async checksum workers. Repair writes intentionally bypass normal mirrored submission to update only the bad copy, so mirror mapping and device lifetime protection through the bio counter are critical.
