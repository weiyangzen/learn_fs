# sources/test-tools/fio/os/os-windows.h

## Purpose
`os-windows.h` adapts fio to Windows by declaring POSIX-like shims, Windows feature support, direct/open flag placeholders, path and clock defaults, device sizing, memory and random seed helpers, scheduling, mkdir emulation, and CPU affinity APIs.

## Important APIs, Types, and Functions
It defines `FIO_OS os_windows`, `FIO_HAVE_ODIRECT`, `FIO_HAVE_CPU_AFFINITY`, `FIO_HAVE_CHARDEV_SIZE`, `FIO_HAVE_GETTID`, `FIO_EMULATED_MKDIR_TWO`, `FIO_PREFERRED_ENGINE "windowsaio"`, path separator `\\`, signal and fcntl placeholders, POSIX prototypes, and helpers `blockdev_size()`, `chardev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `gettid()`, `init_random_seeds()`, `fio_set_sched_idle()`, and `fio_mkdir()`.

## Control Flow
`blockdev_size()` uses an existing `HANDLE` or opens the path with `CreateFile()`, then calls `DeviceIoControl(IOCTL_DISK_GET_LENGTH_INFO)`. Random seeds come from `CryptAcquireContext()` and `CryptGenRandom()`. `fio_mkdir()` checks existing directory attributes, calls `CreateDirectoryA()`, and maps Windows errors to POSIX errno except for the device namespace case.

## State and Persistence
Helpers may open/close handles, create directories, change thread priority, and fill random seed buffers. The header itself has no static state.

## Dependencies and Integration Points
It depends on Winsock, Windows, PSAPI, fio Windows POSIX shims, `smalloc`, debug/log helpers, hweight, and `os-windows-7.h`. Its declarations are used by fio core, file setup, random initialization, scheduler-idle support, and Windows async I/O engine paths.

## Risks and Edge Cases
`O_DIRECT` and `O_SYNC` are placeholder bits for runtime rejection outside Windows native open paths. `blockdev_size()` must handle the difference between POSIX fd-backed files and Windows handles. Many POSIX functions are declared here but implemented elsewhere, so link coverage matters. `sysconf()` values are shim-defined.

## Test Signals
Windows builds, `windowsaio` smoke tests, raw disk size checks, random seed initialization failure handling, mkdir behavior for existing directories and `\\.` namespace, and CPU affinity tests validate this adapter.
