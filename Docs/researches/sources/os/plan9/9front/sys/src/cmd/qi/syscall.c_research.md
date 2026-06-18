# File Research: sources/os/plan9/9front/sys/src/cmd/qi/syscall.c

Host syscall bridge for simulated Power Plan 9 programs running under `qi`.

Key responsibilities:
- Maps Plan 9 syscall numbers to names and handler functions.
- Implements supported syscalls by reading arguments from the simulated stack, copying strings/buffers via `memio`, invoking host Plan 9 libc/syscalls, writing results back, and setting `reg.r[REGRET]`.
- Supported operations include errstr, bind, chdir, close, dup, exits, open, read/pread, write/pwrite, seek/oseek, rfork without `RFPROC`, sleep, old/new stat/fstat, pipe, create, fd2path, brk, remove, notify, and segflush.
- Unsupported syscalls print “No system call” and exit.
- `sc` validates the syscall instruction encoding, dispatches through `systab`, traces if enabled, and flushes output.

Dependencies and coupling:
- Includes Plan 9 syscall number header `/sys/src/libc/9syscall/sys.h`.
- Uses simulated memory accessors, `errbuf`, `bioout`, register state, and host filesystem/process APIs.

Filesystem/OS relevance:
- This is the main OS boundary for `qi`: simulated file descriptors and filesystem calls are forwarded to the host Plan 9 environment.
