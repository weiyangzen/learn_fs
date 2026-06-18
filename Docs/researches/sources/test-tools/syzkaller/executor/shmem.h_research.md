# sources/test-tools/syzkaller/executor/shmem.h

Purpose: RAII wrapper for shared memory regions used by runner request/response buffers and coverage filters.

Important APIs and control flow: `ShmemFile(size)` creates a `mkstemp` file, `ftruncate`s it, mmaps it read/write, and unlinks the name. `ShmemFile(fd, preferred, size, write)` maps an existing fd at an optional preferred address with read-only or read/write protections. The destructor unmaps and closes owned fds. `Seal` mprotects the mapping read-only and closes the fd. `FD` and `Mem` expose the backing fd and mapped pointer.

State and dependencies: owns `mem_`, `size_`, and `fd_`. Uses POSIX `mkstemp`, `ftruncate`, `mmap`, `munmap`, `mprotect`, `unlink`, and `close`.

Integration points: `executor_runner.h` uses it for request/response shmem; `CoverFilter` stores its table in a `ShmemFile`.

Risks and tests: `Seal` closes the fd, so callers must duplicate/pass fds before sealing if needed. Mapping failures are fatal. OpenBSD lacks `fallocate`, hence `ftruncate` is the portable sizing method. Indirectly tested through runner and cover-filter tests.
