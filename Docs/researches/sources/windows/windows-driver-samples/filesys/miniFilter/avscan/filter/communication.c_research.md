# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/communication.c

Kernel/user communication implementation for the AV minifilter. It creates and manages Filter Manager communication ports, handles client connect/disconnect callbacks, validates user messages, dispatches scan commands, and maps user-provided file handles back to stream contexts for query operations.

Key responsibilities:
- `AvPrepareServerPort` creates one named server port for scan, abort, or query traffic using names from `avlib.h`.
- `AvConnectNotifyCallback` accepts exactly one connection per type, copies the connection type into a cookie, and records the client port in `Globals`.
- `AvDisconnectNotifyCallback` closes the matching client port and frees the connection cookie.
- `AvMessageNotifyCallback` handles `AvCmdCreateSectionForDataScan`, `AvCmdCloseSectionForDataScan`, and `AvIsFileModified`.
- `AvGetScanCtxSynchronized` validates scan IDs by searching the global active scan list under `Globals.ScanCtxListLock` and references the scan context while in use.
- `AvHandleCmdCreateSectionForDataScan` creates a section context and Filter Manager data-scan section, marks stream state as scanning, stores the section context in the scan context, and returns a user-mode section handle.
- `AvHandleCmdCloseSectionForDataScan` records the scanner’s result, finalizes scan/section state, and releases waiting I/O.
- `AvUpdateStreamContextWithScanResult` transitions stream or transaction state from scanning to infected/clean, or back to modified if undetermined.
- `AvGetInstanceContextByFileHandle` and `AvGetStreamContextByHandle` support query-port file-handle lookups.

Protocol behavior:
- User mode starts from a scan notification sent by `scan.c`, then sends create-section and close-section commands back to this callback.
- Output buffers are checked for size and alignment before handle/boolean writes.
- User buffers are accessed inside exception handling using `AvExceptionFilter`.
- If writing the section handle back to user mode fails, the kernel closes the handle with `NtClose` and finalizes the scan to avoid leaks and blocked I/O.

Concurrency and lifecycle notes:
- Section finalization uses interlocked pointer exchange so only one racing thread tears down the section.
- `AvFinalizeScanContext` always signals `ScanCompleteNotification`.
- Section finalization calls `AvCloseSectionForDataScan` and releases the Filter Manager section context reference.
- `AvHandleCmdCreateSectionForDataScan` handles cancellation both before and after section creation.

Dependencies:
- Filter Manager communication ports, section data scan APIs, object handle referencing, active scan context helpers from `avscan.h`, stream/instance context helpers from `context.c`, and shared command structures from `avlib.h`.

Research notes:
- The file-modified query reports only `IS_FILE_MODIFIED(streamContext)`, not infected or transaction-modified state.
- The design assumes one client connection per port type.
