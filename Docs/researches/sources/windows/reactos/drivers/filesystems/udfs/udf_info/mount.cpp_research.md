# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/mount.cpp

## Purpose
Implements UDF mount, verification, and unmount metadata handling. It discovers anchors and volume recognition sequences, processes main/reserve volume descriptor sequences, loads partition maps and file sets, builds internal free/zero-space bitmaps, loads sparing/VAT-related state, and flushes updated volume metadata on unmount.

## Key Elements
- `UDFFindAnchor` probes expected anchor locations, VAT-related tail locations, and MRW workaround offsets, registering valid anchors and forcing read-only mode when MRW addressing problems are detected.
- `UDFFindVRS` scans the volume recognition sequence for ISO9660, BEA01/TEA01, NSR02, and NSR03 signatures.
- `UDFReadVDS`, `UDFProcessSequence`, and `UDFVerifySequence` scan descriptor sequences, follow multipart `VolDescPtr` chains, and dispatch descriptor-specific load/verify routines.
- `UDFLoadLogicalVol` initializes logical block size, reads UDF domain flags, parses type 1/type 2 partition maps, detects virtual, sparable, and metadata partitions, and loads the logical volume integrity descriptor.
- `UDFLoadPartDesc`, `UDFBuildFreeSpaceBitmap`, `UDFAddXSpaceBitmap`, and verification counterparts populate or validate in-memory allocation/zero bitmaps from partition headers, unallocated/freed space bitmaps, and unallocated-space descriptors.
- `UDFLoadLogicalVolInt` walks LVID chains, keeps the last valid descriptor, imports revision/file/dir counters, and applies partial-damage policy.
- `UDFLoadSparingTable` merges sparing table entries from all advertised table locations and records relocation metadata.
- `UDFFindLastFileSet` follows file-set descriptor chains and `UDFLoadFileset` stores root and system stream ICB locations plus volume identity.
- `UDFUmount__` flushes cached allocations, handles CDR/VAT recording, updates bad-block/non-allocatable state, updates volume labels, VDS bitmaps, sparing tables, and LVID close state.

## Dependencies
Depends on `udf.h`, UDF/ECMA descriptor layouts, dstring helpers in this file plus Unicode compression/decompression elsewhere, extent I/O (`UDFReadExtent`, `UDFWriteExtent`), bitmap helpers, sparing/VAT helpers, write cache helpers, tagged descriptor read/write helpers, and VCB policy/configuration fields.

## Behavior/Risks
Mount behavior is tolerant and policy-driven: corrupt main VDS can fall back to reserve VDS, damaged LVID can trigger read-only, raw-disk, or risky read/write mode, and missing anchors on CD media lead to CDFS/zero-buffer checks. Unmount only writes metadata when the volume is writable and modified.

Risk areas include complex recovery fallbacks, many global VCB side effects, manual pool ownership across SEH blocks, descriptor length trust boundaries, and duplicated load/verify code paths that can drift. The sparing-table merge code is subtle and contains suspicious duplicate-location indexing in the already-processed check. Metadata writeback depends on the internal free-space bitmap accurately reflecting every allocation mutation made elsewhere.
