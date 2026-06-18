<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/ld_sockerr.c -->
# sources/user-network-fs/libsmb2/tests/ld_sockerr.c

Purpose: LD_PRELOAD helper that injects socket read failures into libsmb2 tests by interposing `readv`.

Important APIs, types, and functions: Defines global `readv_close` and replacement `readv` that resolves the real function with `dlsym(RTLD_NEXT)`, reads `READV_CLOSE`, increments a call counter, writes garbage and returns `-1`/`EBADF` on the selected call.

Control flow: On first call it initializes the real `readv` pointer and target failure index. Subsequent calls pass through until the configured call count, then simulate a broken socket.

State and persistence behavior: State is process-local static `call_idx`, function pointer, and global target index. No persistence across processes.

Dependencies and integration points: Built into `ld_sockerr.so` by `tests/Makefile.am` and used by socket-error shell tests through `LD_PRELOAD`.

Risks: Interposing `readv` is platform-sensitive and can affect non-SMB file descriptors in the process. Writing garbage to the fd before failing may trigger behavior different from a pure disconnect.

Test signals: Covered by ls/cp/cat socket-error tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/ld_sockerr.c -->
