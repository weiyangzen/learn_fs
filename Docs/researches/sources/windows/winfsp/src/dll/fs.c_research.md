# File Research: sources/windows/winfsp/src/dll/fs.c

Core `FSP_FILE_SYSTEM` object lifecycle, mount management, dispatcher threading, and notification wrappers.

Key responsibilities:
- Allocates a TLS key for per-dispatcher operation context.
- Preflights device and mount-point availability.
- Creates and deletes WinFsp file system objects.
- Opens the driver volume through `FspFsctlCreateVolume`.
- Installs the default operation dispatch table for all transaction kinds.
- Sets and removes mount points through `FspMountSet`/`FspMountRemove`.
- Starts, stops, and supervises dispatcher threads.
- Sends synchronous and asynchronous responses back to the driver.
- Wraps notification begin/end/send APIs.

Important behavior:
- Default dispatcher thread count is based on process affinity and clamped to 4-16, with a hard minimum of 2.
- The dispatcher creates additional dispatcher threads recursively until the requested count is reached.
- Each dispatcher owns request and response buffers and places them in TLS as `FSP_FILE_SYSTEM_OPERATION_CONTEXT`.
- Requests are received and responses are sent through `FspFsctlTransact`.
- Each valid transaction is guarded by `EnterOperation`/`LeaveOperation`, dispatched via `FileSystem->Operations[Kind]`, optionally logged, aligned, and returned.
- `STATUS_PENDING` clears the immediate response so async completion can later use `FspFileSystemSendResponse`.
- `FspFileSystemStopDispatcher` marks an internal stopping bit, stops the driver transaction path, waits for the dispatcher, and then issues the final stop.

Dependencies:
- Includes `dll/library.h`.
- Depends on `fsop.c` operation entry points, `fsctl.c` driver calls, mount helpers, memory helpers, debug logging, TLS, SRW locks, and Windows threading APIs.

Notable risks:
- Dispatcher shutdown and async response paths depend on correct stop ordering.
- Some state bits are manipulated through packed/interlocked access to adjacent structure fields, so layout compatibility matters.
