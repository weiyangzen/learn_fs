# File Research: sources/windows/reactos/drivers/filesystems/fastfat/dumpsup.c

## Purpose

`dumpsup.c` is a `FASTFATDBG`-only debugging support module for dumping in-memory FastFAT structures through `DbgPrint`. It is compiled only when `FASTFATDBG` is defined and has no retail/runtime filesystem behavior.

## Main Contents

- `FatDump(PVOID Ptr)` dispatches by `NodeType(Ptr)` to the right dump routine:
  - `FAT_NTC_DATA_HEADER` -> `FatDumpDataHeader`
  - `FAT_NTC_VCB` -> `FatDumpVcb`
  - `FAT_NTC_FCB`, `FAT_NTC_DCB`, `FAT_NTC_ROOT_DCB` -> `FatDumpFcb`
  - `FAT_NTC_CCB` -> `FatDumpCcb`
- `FatDumpDataHeader()` prints global `FatData` fields and walks `FatData.VcbQueue`, dumping each `VCB`.
- `FatDumpVcb(PVCB Ptr)` prints volume state, allocation support fields, section object pointers, dirty/free cluster tracking, and then dumps the root DCB.
- `FatDumpFcb(PFCB Ptr)` prints file/directory control block state, names, allocation/file size fields, section object pointers, and recursively dumps child FCBs for DCB/root DCB nodes.
- `FatDumpCcb(PCCB Ptr)` prints CCB node metadata, query template text, and search offset.

## Formatting Helpers

The file defines local dump macros:

- `DumpNewLine` resets the current dump column.
- `DumpLabel` prints a shortened field label, preferring text after the last dot in nested field names.
- `DumpField` prints pointer/integer-like fields with fixed spacing.
- `DumpListEntry` prints `Flink` and `Blink`.
- `DumpName` copies a fixed-width character buffer into a local string for output.
- `TestForNull` rejects null pointers before dereferencing.

## Notable Details

- Recursive dumping follows the live VCB/FCB tree, so corrupted list links could make debug dumps recurse or walk bad memory.
- `DumpField` uses `%p` for all fields, including non-pointer scalar fields. This is acceptable for debug output but not semantically typed.
- `DumpName` copies fixed-width data without checking the actual string length. It is meant for diagnostic snapshots, not safe user-visible formatting.
- There is no synchronization. Callers are expected to use it only in debugging contexts where concurrent mutation is understood.

## Integration

This module is tied to `DebugDump` in `fatdata.h`, which calls `FatDump(PTR)` when debug tracing is enabled and then asserts. It provides introspection over core FastFAT structures defined elsewhere in the driver.
