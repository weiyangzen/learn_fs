# File Research: sources/windows/reactos/drivers/filesystems/udfs/udffs.h

This is the main include file for the ReactOS UDF filesystem driver. It centralizes compile-time feature switches, NT kernel dependencies, core UDF headers, public IOCTL definitions, debug helpers, resource wrappers, exception helpers, and file-specific bug-check IDs.

Key contents:
- Feature options include HDD support, extended attributes, sparse files, packed directories, hardlinks, delayed close, rename/move support, and optional security/read-only-related behavior.
- Default tuning constants cover directory packing, readahead granularity, sparse threshold, mount error threshold, bitmap/tree flush timeouts, and per-CPU FSP thread counts.
- `UDF_VALID_FILE_ATTRIBUTES` defines the supported Windows file attribute mask, including sparse-file support when enabled.
- Kernel includes pull in `ntifs.h`, ReactOS cross-NT support, mount manager definitions, physical I/O helpers, registry helpers, memory helpers, and UDF internals.
- Exports the global `UDFGlobalData` and `DefLetter`.
- Provides control-flow macros such as `try_return`, flag helpers, alignment helpers, and `UDFPanic`.
- `UdfIllegalFcbAccess` rejects write/security-style access on read-only volumes or when write-security is disabled.
- `UDFPrint`/`UDFPrintErr` and the resource/interlocked macros switch between direct kernel primitives and debug wrappers depending on `UDF_DBG`.
- `UDFRaiseStatus` and `UDFNormalizeAndRaiseStatus` save exception status in the IRP context before raising.
- Defines unique `UDF_FILE_*` bug-check IDs used by individual implementation files.

Notable design points:
- This file is the driver’s compile-time configuration surface. Many later `.cpp` files change behavior through symbols defined here.
- Resource operations are abstracted so debug builds can track acquisition site and file bug-check ID without changing call sites.
- The header supports both kernel and `_CONSOLE` builds, but most included paths and dispatch prototypes target kernel-mode FSD operation.
