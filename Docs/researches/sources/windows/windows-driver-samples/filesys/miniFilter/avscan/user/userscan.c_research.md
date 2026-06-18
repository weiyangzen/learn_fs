# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/userscan.c

## Purpose

Implements the user-mode scanner side of the `avscan` minifilter sample. The scanner connects to kernel filter communication ports, runs a fixed pool of scan worker threads, maps sections created by the filter for file data, scans memory for an encoded test signature, sends scan results back to the filter, and listens for abort/unload notifications.

## Public And Internal APIs

- Exported by `userscan.h`: `UserScanInit()` and `UserScanFinalize()`.
- Thread procedures: `UserScanWorker()` handles scan messages from the scan port; `UserScanListenAbortProc()` handles abort and unload notifications from the abort port.
- Scan helpers: `UserScanMemoryStream()` decodes and searches the sample malware pattern; `UserScanHandleStartScanMsg()` drives the create-section, map, scan, unmap, close-section protocol.
- Cleanup helpers: `UserScanSynchronizedCancel()`, `UserScanClosePorts()`, `UserScanCleanup()`, `WaitForAll()`.
- Lookup helper: `UserScanGetThreadContextById()` maps a scan thread ID to its `SCANNER_THREAD_CONTEXT`.

## Control Flow

- `UserScanInit()` creates one suspended abort-listener thread and six suspended scan-worker threads, initializes per-worker critical sections, connects to `AV_SCAN_PORT_NAME` with `AvConnectForScan`, attaches the scan port to an IO completion port, stores handles in the caller-provided `USER_SCAN_CONTEXT`, resumes threads, then posts one overlapped `FilterGetMessage()` per worker.
- Scan messages use `SCANNER_MESSAGE`, which embeds `FILTER_MESSAGE_HEADER`, `AV_SCANNER_NOTIFICATION`, and an `OVERLAPPED` so `GetQueuedCompletionStatus()` can recover the owning message via `CONTAINING_RECORD`.
- `UserScanWorker()` waits on the IO completion port, replies to `AvMsgStartScanning` with the worker thread ID, records `ScanId`, calls `UserScanHandleStartScanMsg()`, then reposts the same message with `FilterGetMessage()`.
- `UserScanHandleStartScanMsg()` sends `AvCmdCreateSectionForDataScan`, maps the returned section read-only, queries the mapped region size, calls `UserScanMemoryStream()`, optionally uses `MEM_UNMAP_WITH_TRANSIENT_BOOST` for open-triggered scans, unmaps, closes the section handle, and sends `AvCmdCloseSectionForDataScan` with the scan result.
- `UserScanListenAbortProc()` connects separately to `AV_ABORT_PORT_NAME` with `AvConnectForAbort`; `AvMsgAbortScanning` finds the target worker and sets its abort flag only if the `ScanId` still matches; `AvMsgFilterUnloading` cancels workers, replies to the filter, closes ports, closes the abort port, and terminates the process.
- `UserScanFinalize()` sets `Context->Finalized`, marks every worker aborted, calls `CancelIoEx()` on the scan connection port, waits for all scan workers, then closes ports/thread handles and frees worker contexts.

## State And Data Structures

- `USER_SCAN_THREAD_COUNT` is fixed at six.
- `SCANNER_MESSAGE_SIZE` deliberately excludes the embedded `OVERLAPPED`; it is used for synchronous abort-port messages and overlapped scan-port receive lengths.
- `SCANNER_REPLY_MESSAGE` replies with the worker thread ID so the kernel filter can associate a scan request with the user-mode thread servicing it.
- Per-worker state comes from `SCANNER_THREAD_CONTEXT`: thread handle, thread ID, current `ScanId`, abort flag, and a critical section.
- Shared state comes from `USER_SCAN_CONTEXT`: worker array, abort thread handle, finalize flag, filter connection port, and IO completion port.

## Dependencies

- User-mode Windows APIs: `CreateThread`, `ResumeThread`, `CreateIoCompletionPort`, `GetQueuedCompletionStatus`, `HeapAlloc`, `HeapFree`, `MapViewOfFile`, `VirtualQuery`, `UnmapViewOfFileEx`, `CloseHandle`, `CancelIoEx`, `WaitForMultipleObjects`, `ExitProcess`.
- Filter manager user APIs: `FilterConnectCommunicationPort`, `FilterGetMessage`, `FilterReplyMessage`, `FilterSendMessage`.
- Shared protocol from `avlib.h`: port names, connection types, command IDs, notification fields, scan reasons, scan IDs, and `AVSCAN_RESULT`.

## Risks And Invariants

- Scan message buffers are heap-allocated in `UserScanInit()` and owned by workers after completion-port delivery; each worker frees its current message on exit.
- `ScanId` and `Aborted` updates are protected when reset/set, but `UserScanMemoryStream()` polls `Aborted` directly through a pointer while scanning. This is acceptable for a sample but not a strongly synchronized cancellation primitive.
- `Context->Finalized` is also read by workers without synchronization.
- On filter unload, the abort listener calls `ExitProcess(0)`, so normal caller-controlled cleanup may be bypassed.
- The code assumes kernel/user protocol ordering: a scan worker must reply with its thread ID before asking the filter to create a section, and must always send `AvCmdCloseSectionForDataScan` after creating a section so the filter can release waiting I/O and update file state.
- `hEvent` in `UserScanInit()` is initialized and cleaned up but never assigned or used.
