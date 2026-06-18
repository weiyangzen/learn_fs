# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/syscall.c

Purpose: Emulates Plan 9 MIPS system calls on the host.

Key behavior:
- Maps syscall numbers to names and handler functions.
- Implements common file/process-memory syscalls including errstr, fd2path, bind, chdir, close, dup, exits, open, read/pread, seek/oseek, rfork without RFPROC, sleep, stat/fstat old and new forms, write/pwrite, pipe, create, brk, remove, notify, and segflush.
- Copies syscall arguments/results between simulated stack/memory and host buffers.
- Unimplemented syscalls print a message and exit.

Dependencies:
- Uses `/sys/src/libc/9syscall/sys.h`, memory accessors, simulated registers, host Plan 9 syscalls, and debugger tracing.

Notable details:
- Many namespace/process syscalls are stubs, so simulated programs using mount, wait, exec, segment attach/detach, rendezvous, etc. will stop.
