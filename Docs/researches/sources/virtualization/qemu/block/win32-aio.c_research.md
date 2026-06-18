# File Research: sources/virtualization/qemu/block/win32-aio.c

Windows asynchronous I/O backend for QEMU raw/block file operations. It wraps Windows overlapped I/O and IO completion ports into QEMU’s AIO callback model.

Key responsibilities:
- Maintain `QEMUWin32AIOState` with IOCP handle, event notifier, in-flight count, and attached `AioContext`.
- Represent each request with `QEMUWin32AIOCB`, including overlapped state, request context, QEMUIOVector, temporary linear buffer, operation type, and result.
- Submit reads/writes through `ReadFile()`/`WriteFile()` with `OVERLAPPED`.
- Use a temporary block-aligned buffer for multi-iovec requests, copying into/out of the QEMU iovec as needed.
- Process IOCP completions from `win32_aio_completion_cb()`, complete callbacks in the original request `AioContext`, and free AIOCBs.
- Attach file handles to an IOCP and attach/detach event notifier handling from QEMU AIO contexts.
- Initialize and clean up the backend state.

Important functions:
- `win32_aio_submit()`: creates AIOCB, prepares buffer and overlapped offset, starts Windows async read/write, and returns `BlockAIOCB`.
- `win32_aio_process_completion()`: translates Windows completion to QEMU status, zero-pads short reads, rejects short writes, copies read data back for non-linear buffers, and schedules callback.
- `win32_aio_attach()`: binds a Windows handle to the IOCP.
- `win32_aio_init()` / `win32_aio_cleanup()`: lifecycle management.

Notable constraints and risks:
- Short reads are treated as EOF and zero-filled; short writes are errors.
- Completion callback execution is redirected when the completing backend context differs from the original request context.
- The file is Windows-specific and depends on `<windows.h>`, `<winioctl.h>`, event notifiers, and QEMU AIO internals.
