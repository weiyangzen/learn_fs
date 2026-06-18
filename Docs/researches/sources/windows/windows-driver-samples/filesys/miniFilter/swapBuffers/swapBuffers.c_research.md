# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/swapBuffers/swapBuffers.c

## Scope And Role

`swapBuffers.c` is a Windows Filter Manager mini-filter sample showing how to replace user I/O buffers with filter-owned buffers for read, write, and directory-control operations, then copy data back or free state in post-operation callbacks.

The sample is mostly about correct buffer handling across IRP, Fast I/O, MDL, system-buffer, arbitrary user-buffer, cached, and non-cached paths.

Read coverage: full file, 2,325 lines.

## Main State

Global state includes:

- `gFilterHandle`: registered filter handle.
- `Pre2PostContextList`: nonpaged lookaside list for passing state from pre-op to post-op.

Key structures:

- `VOLUME_CONTEXT`: per-volume context with display name and sector size.
- `PRE_2_POST_CONTEXT`: holds the referenced volume context and swapped buffer pointer for post-op cleanup.

Pool tags identify buffer swaps, volume contexts, names, and pre/post state.

## Registration And Volume Setup

The filter registers callbacks for:

- `IRP_MJ_READ`: `SwapPreReadBuffers` / `SwapPostReadBuffers`
- `IRP_MJ_WRITE`: `SwapPreWriteBuffers` / `SwapPostWriteBuffers`
- `IRP_MJ_DIRECTORY_CONTROL`: `SwapPreDirCtrlBuffers` / `SwapPostDirCtrlBuffers`

`InstanceSetup` attaches broadly to volumes. It allocates a volume context, reads volume properties, stores a sector size with a minimum of `0x200`, and tries to derive a display name:

1. Prefer DOS name from `IoVolumeDeviceToDosName`.
2. Fall back to real device name or filesystem device name from `FLT_VOLUME_PROPERTIES`.
3. Append `:` to fallback names for display.

`CleanupVolumeContext` frees the allocated name buffer. `InstanceQueryTeardown` always allows detach.

`DriverEntry` initializes pool NX opt-in, reads `DebugFlags`, initializes the lookaside list, registers the filter, and starts filtering. `FilterUnload` unregisters and deletes the lookaside list.

## Read Buffer Swap Flow

`SwapPreReadBuffers`:

1. Skips zero-length reads.
2. Gets the volume context.
3. Rounds non-cached read length up to the volume sector size.
4. Allocates an aligned nonpaged replacement buffer with `FltAllocatePoolAlignedWithTag`.
5. Builds an MDL for IRP operations, but not Fast I/O.
6. Allocates a pre/post context.
7. Replaces `ReadBuffer` and `MdlAddress`, calls `FltSetCallbackDataDirty`, and requests a post callback.

`SwapPostReadBuffers`:

- If the read failed or returned zero bytes, it only cleans up.
- If the original request has an MDL, it maps it with `MmGetSystemAddressForMdlSafe`.
- If the original buffer is a system buffer or Fast I/O buffer, it copies directly with exception handling.
- For arbitrary user buffers without MDLs, it calls `FltDoCompletionProcessingWhenSafe` and delegates to `SwapPostReadBuffersWhenSafe`.

`SwapPostReadBuffersWhenSafe` locks the user buffer with `FltLockUserBuffer`, maps the resulting MDL, copies data from the swapped buffer, and frees all pre/post state.

## Directory Control Buffer Swap Flow

`SwapPreDirCtrlBuffers` handles query-directory buffers:

1. Skips zero-length query-directory buffers.
2. Gets the volume context.
3. Allocates a zeroed nonpaged replacement buffer with `ExAllocatePoolZero`.
4. Always builds an MDL because directory-control operations are IRP-based.
5. Replaces `DirectoryBuffer` and `MdlAddress`, marks callback data dirty, stores pre/post state, and asks for a post callback.

`SwapPostDirCtrlBuffers` mirrors the read post path, with MDL/system/Fast I/O/arbitrary-user-buffer handling and safe-post fallback.

A notable sample behavior: for directory-control copy-back, it copies the original query buffer length rather than `IoStatus.Information`. The comments say this works around a FASTFAT bug where the information length can be short, but also call out the security implication: the replacement buffer must be clean before calling the filesystem to avoid exposing stale data. This implementation uses `ExAllocatePoolZero`, satisfying that sample constraint.

`SwapPostDirCtrlBuffersWhenSafe` performs the safe-IRQL arbitrary-buffer copy-back after `FltLockUserBuffer`.

## Write Buffer Swap Flow

`SwapPreWriteBuffers`:

1. Skips zero-length writes.
2. Gets the volume context.
3. Rounds non-cached write length up to sector size.
4. Allocates an aligned replacement buffer.
5. Builds an MDL for IRP operations.
6. Resolves the original write buffer from its MDL when present, otherwise uses `WriteBuffer`.
7. Copies user data into the replacement buffer inside `try/except`.
8. Replaces `WriteBuffer` and `MdlAddress`, marks callback data dirty, stores pre/post state, and requests a post callback.

If it cannot map the original MDL or copying raises an exception, it completes the operation with failure from the pre-op path.

`SwapPostWriteBuffers` does not copy data back. It logs, frees the aligned swapped buffer, releases the volume context, frees the lookaside context, and finishes processing.

## Resource Handling

The file consistently cleans up allocations when a pre-op path decides not to request a post callback. Post callbacks own cleanup once `FLT_PREOP_SUCCESS_WITH_CALLBACK` is returned.

Important ownership rules visible in the implementation:

- Filter-allocated aligned read/write buffers are freed with `FltFreePoolAlignedWithTag`.
- Directory-control buffers allocated with `ExAllocatePoolZero` are freed with `ExFreePool`.
- MDLs allocated for replacement buffers are generally left for Filter Manager to free after swapped I/O completion, matching the sample comments.
- Volume contexts are acquired in pre-op and released in post-op because post-op may run at DPC where acquiring the context would be unsafe, but releasing is allowed.
- The pre/post context is allocated from and returned to `Pre2PostContextList`.

## Important Risks And Edge Cases

- The read/write non-cached path rounds the allocated buffer length up to sector size. For writes, the code copies `writeLen` bytes from the original buffer after rounding. If the original supplied buffer is only the unrounded length, this sample pattern can read past the logical caller buffer unless the I/O contract guarantees sector-sized backing for non-cached writes.
- Directory-control post deliberately copies the full original query length rather than `IoStatus.Information`. This depends on the swapped buffer being zero-filled, which this file does, but the pattern is risky if reused with uninitialized buffers.
- The code asserts no chained MDLs for read/write original buffers. It is sample-level behavior and may not cover all production stack cases.
- Fast I/O paths avoid replacement MDLs because the Fast I/O interface has no MDL parameter, so correctness depends on direct buffer validity and exception handling.
- Arbitrary user-buffer copy-back depends on `FltDoCompletionProcessingWhenSafe`; if safe posting is unavailable, the operation is failed.
- Logging is controlled by `DebugFlags` but defaults to disabled.

## Integration Points

The file demonstrates several Filter Manager buffer APIs and kernel memory APIs:

- `FltAllocatePoolAlignedWithTag` / `FltFreePoolAlignedWithTag`.
- `FltSetCallbackDataDirty`.
- `FltDoCompletionProcessingWhenSafe`.
- `FltLockUserBuffer`.
- `FltGetVolumeContext`, `FltSetVolumeContext`, `FltReleaseContext`.
- `MmGetSystemAddressForMdlSafe`, `IoAllocateMdl`, `MmBuildMdlForNonPagedPool`.
- Registry debug flag reads through `ZwOpenKey` and `ZwQueryValueKey`.

## Testing Notes

Useful focused tests would cover:

- Cached and non-cached read/write buffer swaps.
- Zero-length read/write/query-directory pass-through.
- IRP path with replacement MDL creation.
- Fast I/O path without replacement MDL.
- Original buffer with MDL, system buffer, and arbitrary user buffer.
- Safe-post copy-back path via `FltDoCompletionProcessingWhenSafe`.
- Failure paths for allocation, MDL allocation, MDL mapping, and user-buffer locking.
- Directory-control copy-back with short `IoStatus.Information` and zero-filled tail behavior.
- Multiple instances/volumes and volume-context cleanup on detach/unload.
