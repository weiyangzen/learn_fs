# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/debug.c

This file contains debug-only tracing plus allocation wrappers used in both debug and non-debug builds. Under `EXT2_DEBUG`, it provides formatted debug printing, IRP call/complete tracing, NTSTATUS stringification, MCB reference tracing, and guarded pool allocation. Without `EXT2_DEBUG`, only direct pool wrappers remain.

Debug-only globals and tables:
- `DebugFilter = DL_DEFAULT`
- `ProcessNameOffset`
- IRP major-function string table.
- File information class string table.
- FS information class string table.

Key functions:
- `Ext2Printf`: timestamped debug print with CPU and thread ID.
- `Ext2NiPrintf`: similar non-indented print helper.
- `Ext2GetProcessNameOffset`: scans the current process object for `"System"` to find process-name offset.
- `Ext2DbgPrintCall`: decodes and logs IRP major/minor functions, file names, read/write offsets and flags, file/fs information classes, directory query options, filesystem control codes, device controls, lock operations, cleanup, shutdown, and PNP.
- `Ext2DbgPrintComplete`: logs failed IRP completions with symbolic NTSTATUS names.
- `Ext2NtStatusToString`: large switch mapping many NTSTATUS/RPC/ACPI/CTX/PNP values to string names, defaulting to `STATUS_UNKNOWN`.
- `Ext2TraceMcb`: debug helper to log and mutate MCB reference counts with callsite formatting.
- `Ext2AllocatePool` under `EXT2_DEBUG`: allocates 0x20 bytes extra, stores size metadata, writes start/end guard bytes, and updates global allocation counters under `Ext2MemoryLock`.
- `Ext2FreePool` under `EXT2_DEBUG`: checks metadata and guard bytes, poisons guard regions, updates allocation counters, and frees with tag.
- `Ext2AllocatePool`/`Ext2FreePool` without `EXT2_DEBUG`: thin wrappers over `ExAllocatePoolWithTag` and `ExFreePoolWithTag`.

Research notes:
- Most of the file is diagnostic mapping, especially the NTSTATUS string table.
- Debug pool wrappers can catch buffer underruns/overruns around allocations made through `Ext2AllocatePool`.
- Because `Ext2TraceMcb` changes reference counts while logging, it is not passive tracing; callers must use it only where that side effect is intended.
