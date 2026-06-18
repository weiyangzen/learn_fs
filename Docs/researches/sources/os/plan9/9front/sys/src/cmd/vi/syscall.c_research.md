# File Research: sources/os/plan9/9front/sys/src/cmd/vi/syscall.c

`syscall.c` emulates a subset of Plan 9 system calls for simulated MIPS programs. It decodes arguments from the simulated stack, copies strings/buffers through `memio()`, invokes host Plan 9 syscalls, writes return values to register `r1`, and maintains an emulated error string.

Implemented calls include bind, chdir, close, dup, exits, open, read/pread, seek/oseek, rfork without `RFPROC`, sleep, old/new stat/fstat, write/pwrite, pipe, create, fd2path, brk, remove, notify registration, segflush no-op, and `_nsec`. Many unsupported calls print “No system call” and exit.

`Ssyscall()` dispatches based on `reg.r[1]`, traces names when enabled, and flushes debugger output. This file is the compatibility boundary between simulated user code and the host environment.
