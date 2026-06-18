# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/syscall.c

## Scope

Plan 9 syscall emulation layer for `5i`.

## Behavior

- Defines `arm.h` globals and maps guest syscall numbers to host wrapper functions.
- Implements core file/process-memory calls: errstr, bind, fd2path, chdir, close, dup, exits, open, read/pread, seek/oseek, sleep, old/new stat/fstat, write/pwrite, pipe, create, brk, remove, notify.
- Many more complex syscalls are stubs that print “No system call” and exit.
- `Ssyscall()` dispatches from guest R0 (`REGARG`) and flushes debugger output.

## Dependencies

Includes Plan 9 syscall numbers from `/sys/src/libc/9syscall/sys.h`, uses guest memory APIs, and calls host Plan 9 libc syscalls directly.

## Risks And Invariants

- This is a convenience emulator, not a sandbox: guest open/read/write/remove/bind/chdir operate on the host namespace.
- Several wrappers use fixed 1024-byte path buffers and `memio(..., MemReadstring)` for bounded guest strings.
- `sysfd2path()` appears to write `errbuf` rather than the actual `buf` to guest memory on success.
- Unsupported syscalls terminate the emulator instead of returning `ENOSYS`.
