<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-check/dwarf.go -->
# sources/test-tools/syzkaller/tools/syz-check/dwarf.go

## Purpose

Parallel DWARF struct extraction backend for syz-check.

## Important APIs, Types, and Functions

`parseKernelObject`, `extractCompilationUnits`, `extractOffsets`, `extractStructs`, and `Unit` offset ranges.

## Control Flow

Opens ELF, drops unneeded sections, pipelines compile-unit enumeration, offset extraction, type resolution, and map merging across goroutines based on GOMAXPROCS.

## State and Persistence Behavior

Returns in-memory map of struct names to DWARF types; no writes.

## Dependencies and Integration Points

Uses Go debug/elf,dwarf; parallelism accounts for DWARF type extraction races.

## Risks and Edge Cases

Duplicate names overwrite; assumes top-level DWARF entries are compile units; large vmlinux remains resource-heavy.

## Test Signals

Synthetic ELF/DWARF fixtures plus real vmlinux performance smoke.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-check/dwarf.go -->
