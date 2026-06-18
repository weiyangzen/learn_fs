# File Research: sources/os/linux/linux-stable/fs/udf/super.c

## Summary
Implements UDF filesystem registration, inode cache lifecycle, mount option parsing, VRS/anchor/descriptor-sequence scanning, partition map loading, LVID handling, root mount setup, remount, sync, statfs, and cleanup.

## Main Responsibilities
- Registers the `udf` block filesystem and its `fs_context` operations.
- Parses mount options for block size, session, last block, anchor, uid/gid policy, modes, strictness, deleted/hidden visibility, allocation descriptor style, and charset.
- Scans Volume Structure Descriptors for NSR02/NSR03 and locates anchor descriptors at standard and fallback positions.
- Processes primary, logical, partition, and integrity descriptors from main/reserve descriptor sequences.
- Builds type 1, virtual, sparable, and metadata partition maps.
- Loads VAT, sparing tables, metadata files, allocation bitmap/table state, file set, and root inode.
- Opens/closes Logical Volume Integrity Descriptors for read-write mounts and generates unique IDs.
- Reports filesystem statistics and free-space counts from LVID, bitmaps, or unallocated-space tables.

## Important Behavior
Mount without an explicit block size scans logical block sizes up to 4096. `-EACCES` is propagated specially to indicate a read-write mount is impossible due to write-incompatible media.

Domain identifiers, read/write revision limits, partition access type, unsupported allocation metadata, virtual partitions, and missing/damaged LVID state can force read-only behavior or reject read-write mounts.

Descriptor scanning records the prevailing descriptor by sequence number, then reloads selected descriptors in dependency order: primary volume, logical volume, and partition descriptors.

## Risks
Mount correctness depends on many defensive bounds checks: partition-map table length, partition count, partition extent overflow, LVID sizes, sparing table sizes, packet power-of-two, and descriptor redirection nesting. Broken media often degrades to read-only instead of writable.
