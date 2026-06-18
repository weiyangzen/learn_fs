# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/syscall.c

Plan 9 syscall emulation bridge for PowerPC programs running under `qi`.

Key responsibilities:
- Maps Plan 9 syscall numbers to names and handler functions.
- Copies syscall arguments from simulated stack memory.
- Implements selected calls through host Plan 9 libc: errstr, fd2path, bind, chdir, close, dup, exits, open, read/pread, seek/oseek, rfork without `RFPROC`, sleep, stat/fstat old and new forms, write/pwrite, pipe, create, brk, remove, notify, and segflush.
- Copies buffers and return values back into simulated memory.
- Maintains an emulated `errbuf`.
- Dispatches `sc` only for the expected PowerPC syscall instruction.

Dependencies:
- Uses `/sys/src/libc/9syscall/sys.h`, host libc/syscalls, `memio`, register state, and debugger tracing flags.

Notable risks:
- Many syscalls intentionally print “No system call” and exit.
- `rfork(RFPROC)` is not supported.
- Host-side syscalls affect the host namespace/files, so emulation is not sandboxed.
- Some compatibility code uses old fixed-size stat/errstr layouts.
