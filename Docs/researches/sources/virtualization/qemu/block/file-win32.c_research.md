# File Research: sources/virtualization/qemu/block/file-win32.c

## Purpose
Windows implementation of QEMU's raw `file` and `host_device` block protocol drivers.

## Main State
- `BDRVRawState` stores Windows `HANDLE`, detected type (`file`, `cd`, `harddisk`), drive path, and optional `QEMUWin32AIOState`.
- `RawWin32AIOData` carries thread-pool AIO work: handle, iovecs, byte count, offset, and operation type.
- `BDRVRawReopenState` carries a replacement handle during reopen.

## I/O Model
- For native Windows AIO, `raw_aio_preadv()` and `raw_aio_pwritev()` use `win32_aio_submit()`.
- Otherwise, operations use `thread_pool_submit_aio()` with `aio_worker()`.
- Thread-pool read/write loops over iovecs and uses `ReadFile`/`WriteFile` with an `OVERLAPPED` offset.
- Short reads are treated as EOF and zero-fill the remaining guest buffer.
- Flush uses `FlushFileBuffers()`.

## Opening
`raw_open()`:
- Parses `filename`, `aio`, and `locking`.
- Rejects `locking=on` on Windows.
- Computes access flags and `FILE_FLAG_OVERLAPPED`/`FILE_FLAG_NO_BUFFERING` based on AIO and cache mode.
- Tracks a drive root path for alignment and filesystem queries.
- Opens with `CreateFile(..., OPEN_EXISTING, ...)`.
- Initializes Win32 AIO when requested.
- Marks truncate extension as zero-initialized via `BDRV_REQ_ZERO_WRITE`.

## Alignment and Length
- `raw_probe_alignment()` uses disk geometry, `GetDiskFreeSpace()`, or fallback 512-byte alignment. CD-ROMs use 2048.
- `raw_co_getlength()` handles regular files, CD media size, and hard-disk geometry.
- Allocated size uses `GetCompressedFileSizeA()` if available, then falls back to `_stati64()`.

## Create/Truncate/Reopen
- `raw_co_create()` creates/truncates a sparse file and rejects preallocation and nocow.
- `raw_co_truncate()` uses `SetFilePointer()` and `SetEndOfFile()`, rejecting preallocation.
- Reopen only supports files, not devices; it opens a replacement handle, attaches it to AIO if needed, then commits or aborts.

## Host Device Support
- `find_cdrom()` locates a CD-ROM drive.
- `find_device_type()` classifies `\\.\PhysicalDrive*`, drive letters, fixed/removable drives, and CD-ROMs.
- `hdev_probe_device()` gives priority to `/dev/cdrom` and Windows drive syntax.
- `hdev_open()` maps `/dev/cdrom` and bare drive letters to Windows device paths, rejects native AIO for host devices, opens with `CreateFile()`, and sets type.
- Host-device driver uses the same read/write/flush/length code as regular file driver and marks variable length.

## Registered Drivers
- `bdrv_file`: `file` protocol for regular Windows files.
- `bdrv_host_device`: `host_device` protocol for Windows drives/devices.
