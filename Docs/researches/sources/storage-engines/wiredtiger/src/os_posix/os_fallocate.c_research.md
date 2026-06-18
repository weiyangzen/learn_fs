# sources/storage-engines/wiredtiger/src/os_posix/os_fallocate.c

## Purpose
Selects and installs the best available POSIX file-extension method for a file handle.

## Important APIs, Types, and Functions
Private probes are `__posix_std_fallocate`, `__posix_sys_fallocate`, and `__posix_posix_fallocate`. The exported platform hook is `__wti_posix_file_extend`.

## Control Flow
On the first extend call, `__wti_posix_file_extend` probes `fallocate`, syscall `SYS_fallocate`, `posix_fallocate`, and finally `fh_truncate`. When a method succeeds, it stores either the lock-free `fh_extend_nolock` pointer and clears the locking `fh_extend`, or stores a locking `fh_extend` when required. If no method works, it clears `fh_extend` and returns `ENOTSUP`.

## State and Persistence Behavior
Successful calls extend the underlying file to the requested offset. The first call mutates the file handle's method table so later extensions skip probing and use the selected implementation.

## Dependencies and Integration Points
The file depends on platform feature macros for `fallocate`, `SYS_fallocate`, and `posix_fallocate`, the POSIX file handle type, and the common file-handle method table. It integrates with block manager file preallocation and extension paths.

## Risks and Edge Cases
The comments document Linux systems where `posix_fallocate` corrupted existing data, so Linux keeps it behind the locking function when selected and prefers `fallocate` variants first. The first-call probe is assumed single-threaded because it is configured as a locking call. Memory barriers protect method-table updates visible to other threads.

## Test Signals
Platform tests should cover each configured fallocate method, fallback to truncate, `ENOTSUP` when no method exists, repeated calls after method installation, and data-integrity checks around preallocation.
