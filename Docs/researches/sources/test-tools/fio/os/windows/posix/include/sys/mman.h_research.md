# sources/test-tools/fio/os/windows/posix/include/sys/mman.h

Purpose: declares the memory-mapping subset used by fio on Windows.

Important APIs/types: defines `PROT_*`, `MAP_*`, `MAP_FAILED`, `MS_*`, and declares `mmap()`, `munmap()`, `msync()`, `mlock()`, `munlock()`, and `posix_madvise()`.

Control flow and state: implementations in `posix.c` translate anonymous mappings to `VirtualAlloc()` and file mappings to `CreateFileMapping()`/`MapViewOfFile()`, with cleanup through `UnmapViewOfFile()` or `VirtualFree()`.

Dependencies and integration: included by fio memory allocation and synchronization code that wants Unix APIs. `rwlock.c` uses `mmap()`/`munmap()` through the OS abstraction.

Risks: constants are local shim values and not ABI-compatible with Unix. `MAP_FAILED` is `NULL`, unlike POSIX `(void *)-1`, so callers must be compatible with this behavior. `MAP_FIXED` and several flags are declared but not fully implemented.

Test signals: Windows tests for anonymous mapping, file mapping, sync, lock/unlock, and failure paths.
