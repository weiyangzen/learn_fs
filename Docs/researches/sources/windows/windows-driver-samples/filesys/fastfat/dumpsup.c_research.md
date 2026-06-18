# File Research: sources/windows/windows-driver-samples/filesys/fastfat/dumpsup.c

## Scope And Role

`dumpsup.c` implements debug-only data-structure dump routines for FastFat. All code is compiled only under `FASTFATDBG`; there is no runtime behavior in non-debug builds.

The file is in subset A through `sources/windows/windows-driver-samples`, and was read completely.

## Main Entry Points

- `FatDump`: dispatches by `NodeType(Ptr)` to the right dump routine.
- `FatDumpDataHeader`: dumps global `FatData` and walks the VCB queue.
- `FatDumpVcb`: dumps a volume control block and then dumps its root DCB.
- `FatDumpFcb`: dumps file/directory/root DCB fields and recursively walks child FCB/DCB links for directories.
- `FatDumpCcb`: dumps CCB query-template and enumeration-offset fields.

## Formatting Helpers

The file defines local macros for debug output:

- `DumpNewLine` resets an 80-column style output cursor.
- `DumpLabel` formats field labels by trimming to the last dotted component.
- `DumpField` prints pointer/integer-style fields using `%p`.
- `DumpListEntry` prints `Flink` and `Blink`.
- `DumpName` copies fixed-width character fields to a local buffer.
- `TestForNull` rejects null pointers before dereferencing.

`FatDumpCurrentColumn` tracks output width for layout.

## Data Traversal

`FatDump` recognizes `FAT_NTC_DATA_HEADER`, `FAT_NTC_VCB`, `FAT_NTC_FCB`, `FAT_NTC_DCB`, `FAT_NTC_ROOT_DCB`, and `FAT_NTC_CCB`. Unknown node types print the raw node type code.

`FatDumpDataHeader` starts from global `FatData`, dumps core driver/global fields, then iterates `FatData.VcbQueue` and calls `FatDumpVcb` for each volume. `FatDumpVcb` prints volume allocation/cache/state fields and then dumps `RootDcb`. `FatDumpFcb` prints common FCB fields, name buffers, section object pointers, and either directory-specific child queues or file size. For DCB/root DCB nodes, it recursively dumps each child from `Specific.Dcb.ParentDcbQueue`.

## Integration Points

This file depends on FastFat internal structures and debug macros from `FatProcs.h`, including `PFAT_DATA`, `PVCB`, `PFCB`, `PCCB`, node type codes, list layout, and `DbgPrint`.

## Risks And Test Signals

The code is debug-only and intentionally walks internal linked lists without defensive consistency checks beyond null input. It can recurse deeply through directory trees and assumes structure layouts match the dump fields. Relevant verification is compile-time debug-build coverage plus manual debugger invocation on representative VCB/FCB/CCB objects.
