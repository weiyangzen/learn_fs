# File Research: sources/windows/dokany/dokan/dokan.c

Core Dokan user-mode runtime: initialization, mount lifecycle, driver communication, event pulling/dispatch, completion, open-context lifetime, mount queries, create-flag mapping, and notification APIs.

Key responsibilities:
- Maintains global debug settings, initialization refcount, mounted-instance list, and instance critical section.
- Allocates and destroys `DOKAN_INSTANCE` objects, including device handles, thread-pool cleanup groups, wait handles, keepalive handles, and notify handles.
- Validates drive-letter mount availability and allocation/sector sizes.
- Starts a Dokan mount via `FSCTL_EVENT_START` and maps user options into driver `EVENT_START` flags.
- Opens the per-volume raw device and launches main event-pull workers.
- Dispatches driver events by major function to create, cleanup, close, directory, read, write, information, volume, lock, set-info, flush, and security dispatchers.
- Supports driver log forwarding through `DOKAN_IRP_LOG_MESSAGE`.
- Sends event replies and pulls new batches with `FSCTL_EVENT_PROCESS_N_PULL`.
- Implements both batched event dispatch and dedicated single-event pull loops.
- Allocates event result buffers through default, 16K, 32K, 64K, 128K, or direct allocation paths.
- Tracks `DOKAN_OPEN_INFO.OpenCount`, user context, delayed close filenames, directory cache cleanup, and final `CloseFile` callback.
- Provides public APIs for `DokanInit`, `DokanShutdown`, `DokanMain`, `DokanCreateFileSystem`, `DokanCloseHandle`, wait registration, mount point list retrieval, unmount release FSCTLs, debug mode, mount cleanup, notifications, and create-flag mapping.

Important behavior:
- `DokanCreateFileSystem()` requires prior `DokanInit()` and raises `DOKAN_EXCEPTION_NOT_INITIALIZED` otherwise.
- Main pull-thread count is derived from process affinity, clamped between 2 and 16 unless single-thread mode is enabled.
- Very high CPU counts enable IPC batching automatically.
- `EventCompletion()` currently only releases open info; the dispatch loop later sends `IoEvent->EventResult` back while pulling more work.
- `CloseFile` is invoked only when the open count reaches zero, allowing close to wait for in-flight operations.
- `CheckFileName()` normalizes double-leading backslashes and removes trailing backslash for non-root paths.
- Notifications strip the drive-letter prefix from absolute paths before sending `FSCTL_NOTIFY_PATH`.
- `DokanMapKernelToUserCreateFileFlags()` maps kernel create options/dispositions/access masks back toward Win32 `CreateFile` parameters.

Dependencies:
- Uses Windows threadpool APIs, critical sections, events, handles, `DeviceIoControl`, and mount manager style drive checks.
- Depends on driver public protocol types and FSCTLs from included Dokan public headers.
- Depends on object pools from `dokan_pool.c` and vectors from `dokan_vector.c`.
- Calls dispatchers declared in `dokani.h` and implemented across the Dokan library.

Notable risks:
- `DokanShutdown()` enters `g_InstanceCriticalSection` and then calls `DokanCloseHandle()`, which also enters the same critical section around deletion; this relies on Windows critical sections being recursive for the same thread and on careful list mutation.
- `QueueIoEvent()` does not close the `PTP_WORK` handle after submission in this file; lifetime is presumably tied to cleanup-group closure, but it is not explicit here.
- `SendAndPullEventInformation()` frees event result buffers after IOCTL completion; any later use would be unsafe, so dispatchers must not retain them.
- `DokanGetMountPointList(uncOnly=TRUE)` copies matching entries into original indexes while reporting the unfiltered count, which can leave zeroed gaps in the returned array.
- `CreateDispatchCommon()` can return with `EventResult == NULL`; several dispatchers assume allocation succeeded.
