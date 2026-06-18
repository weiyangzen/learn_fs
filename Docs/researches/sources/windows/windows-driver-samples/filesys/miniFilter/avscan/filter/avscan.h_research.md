# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/avscan.h

Kernel-private umbrella header for the AV minifilter. It enables AVL tables, includes Filter Manager and all local AV modules, defines the global driver state, declares scan-context lifecycle helpers, and provides an inline create-cancellation helper.

Key definitions:
- `AV_SCAN_CONTEXT` tracks one active scan: refcount, instance, file object, completion event, global-list entry, section context, scan ID, user scan thread ID, triggering IRP major function, transaction-writer flag, and abort state.
- `AV_SCANNER_GLOBAL_DATA` stores process-wide minifilter state: scan ID counter, filter pointer, server/client communication ports, active scan list and lock, local/network scan timeouts, debug level, and unloading flag.
- `Globals` is declared as the global instance of `AV_SCANNER_GLOBAL_DATA`.
- Debug trace flags and `AV_DBG_PRINT` wrap `DbgPrint` in checked builds.
- `AvCancelFileOpen` wraps `FltCancelFileOpen`, sets the callback status, and clears information.

Declared interfaces:
- Communication setup and abort notification: `AvPrepareServerPort`, `AvSendAbortToUser`.
- Scan context lifecycle: `AvAllocateScanContext`, `AvReferenceScanContext`, `AvReleaseScanContext`.
- Finalization wrappers: `AvFinalizeScanAndSection`, `AvFinalizeSectionContext`, `AvFinalizeScanContext`.

Dependencies:
- Includes `utility.h`, `context.h`, `scan.h`, `csvfs.h`, and shared protocol header `avlib.h`.
- Requires Filter Manager kernel headers.

Research notes:
- The scan context is intentionally separated from the section context to reduce coupling between I/O request threads and scanner implementation details.
- Global scan-context tracking is central to user-mode command validation: scan IDs sent from user mode are accepted only if found in `Globals.ScanCtxListHead`.
