# File Research: sources/os/plan9/9front/sys/src/cmd/ki/syscall.c

Plan 9 syscall emulation for `ki`. It maps SPARC user register/stack arguments to host Plan 9 libc calls, copying buffers through simulated memory with `memio`. Implemented calls include errstr, fd2path, bind, chdir, close, dup, exits, open, read/pread, seek/oseek, rfork without `RFPROC`, sleep, stat/fstat old and new forms, write/pwrite, pipe, create, brk, remove, notify, and segflush.

Many process/namespace/segment calls intentionally report unsupported and exit. `systab` indexes handlers by `/sys/src/libc/9syscall/sys.h` numbers, and `ta` dispatches traps using return register `R7`, with optional syscall tracing.
