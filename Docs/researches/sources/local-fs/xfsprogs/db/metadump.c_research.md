# File Research: sources/local-fs/xfsprogs/db/metadump.c

## Purpose
Implements the `metadump` command, which copies known XFS metadata into a compact diagnostic image while optionally obfuscating names/attributes and zeroing stale data.

## Main Interfaces
- Registers `metadump` through `metadump_init()`.
- `metadump [-a] [-e] [-g] [-m max_extent] [-w] [-o] [-v 1|2] filename`.
- Supports metadump v1 indexed 512-byte metablocks and v2 extent records with device tags for data, log, and realtime metadata.

## Control Flow
`metadump_f()` validates the mounted superblock, parses options, chooses version, detects external log/realtime metadata needs, checks dirty-log state, opens the output stream or safely redirects stdout, initializes the selected writer, scans every AG, copies the log when supported, optionally copies the realtime superblock, flushes remaining output, restores stdout, releases resources, and clears parent-pointer remap state.

## Metadata Scanning
AG scanning writes the AG superblock, AGF, AGI, AGFL, then recursively copies free-space btrees, rmap/refcount btrees, inode btrees, and inode chunks. Inode processing copies metadata reachable from data and attr forks, including directories, symlinks, attributes, bmbt blocks, quota/realtime metadata files, rt rmap btrees, and rt refcount btrees. It bounds suspicious extents with `max_extent_size`, validates btree levels/counts/pointers, and can continue after read errors unless configured to stop.

## Obfuscation And Redaction
Directory entries, shortform directories, symlink path components, attr names/values, remote attr values, filesystem labels, and realtime labels can be transformed. The code preserves dir/attr hash values via `obfuscate_name()` and avoids obfuscating `lost+found` and numeric orphan names. Parent-pointer filesystems use a remap table so obfuscated dirent names and parent-pointer names remain consistent. Stale-data zeroing clears unused btree slots, unused directory/attr space, unused AGFL slots, free inode literal areas, and clean logs.

## Dependencies
This file is tightly integrated with libxfs/libxlog metadata parsers, xfs_db IO cursor operations, type descriptors, bmap conversion helpers, dir/attr layout helpers, inode geometry, log dirty detection, CRC recalculation through buffer verifiers, and obfuscation helpers.

## Risks And Invariants
- The command intentionally preserves corrupt metadata where possible; verifier failures while recalculating modified CRCs are warnings, not hard stops.
- Dirty logs are copied when necessary and can leak unobfuscated metadata in obfuscated dumps; the code warns about this.
- Metadump v1 cannot include an external log; v2 is selected automatically for external log or realtime-superblock metadata unless the user forces a version.
- Many readers use salvage-mode buffers and defensive bounds checks because source metadata may be corrupt.
