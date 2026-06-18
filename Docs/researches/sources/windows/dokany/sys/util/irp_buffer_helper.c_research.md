# File Research: sources/windows/dokany/sys/util/irp_buffer_helper.c

IRP input/output buffer discovery and size-management helpers for Dokan dispatch code.

Key responsibilities:
- Determines provided input and output buffer sizes from the current IRP stack location.
- Selects the correct input buffer for buffered/direct/neither IOCTL and FSCTL methods.
- Selects the correct output buffer for IOCTL, FSCTL, directory, query information, security, and volume information IRPs.
- Probes user-mode Type3/UserBuffer pointers before kernel access.
- Prepares fixed-size output structures by zeroing and setting `IoStatus.Information`.
- Extends already-prepared output buffers for variable-sized trailing data.
- Appends `UNICODE_STRING` data into variable-sized output structures.

Important behavior:
- For `METHOD_NEITHER` device/file-system controls, input uses `Type3InputBuffer`; output uses `Irp->UserBuffer`.
- Query security and directory control output paths also use user buffers, with directory control preferring an MDL mapping when present.
- `PrepareOutputWithSize` returns `NULL` on undersized buffers and optionally reports the required size through `IoStatus.Information`.
- `ExtendOutputBufferBySize` treats `IoStatus.Information` as the currently reserved size.
- `AppendVarSizeOutputString` validates that `Dest` lies inside the reserved output buffer, extends if needed, and can optionally copy a whole-character partial string like NTFS behavior.

Dependencies:
- Includes `../dokan.h` and `irp_buffer_helper.h`.
- Uses Windows IRP stack structures, `ProbeForRead`, `ProbeForWrite`, MDL mapping, `RtlZeroMemory`, `RtlCopyMemory`, and Dokan exception filtering.

Notable risks:
- `AppendVarSizeOutputString` relies on prior correct reservation via `PrepareOutputWithSize` or equivalent.
- Size arithmetic combines `ULONG`, `ULONG_PTR`, and pointer offsets; call sites must avoid impossible output layouts and reuse of the same destination.
- Probing protects user buffers, but callers still need correct method-specific assumptions about the IRP they are handling.
