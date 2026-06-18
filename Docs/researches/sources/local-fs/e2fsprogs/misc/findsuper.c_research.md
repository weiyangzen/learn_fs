# File Research: sources/local-fs/e2fsprogs/misc/findsuper.c

## Purpose
Standalone raw-device scanner for finding ext2/ext-family superblock signatures.

## Key Elements
Parses optional `-j`, device, skip-byte increment, and starting kilobyte offset. Scans by seeking and reading 512-byte chunks, checking `EXT2_SUPER_MAGIC`, validating basic superblock fields, and printing byte offsets, inferred filesystem start/end, block count, block size, group number, timestamp, UUID prefix, and label.

Tracks duplicate UUID/group-zero superblocks as likely journal copies and hides them unless `-j` is requested. Includes an adaptive progress meter based on elapsed wall time.

## Dependencies
Uses libext2fs superblock structures/helpers, raw `open`, `lseek64`, `read`, NLS support, and ext2 timestamp/string macros.

## Behavior/Risks
Header comments call it a hack and discourage installation. It scans raw devices linearly, can be slow, and only performs heuristic validity checks. Output inference depends on superblock fields and can misidentify journal copies or stale/corrupt metadata.
