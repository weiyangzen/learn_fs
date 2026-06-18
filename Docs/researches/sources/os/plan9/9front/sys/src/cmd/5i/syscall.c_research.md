# File Research: sources/os/plan9/9front/sys/src/cmd/5i/syscall.c

This file implements SWI/system-call handling for the `5i` ARM interpreter by translating guest Plan 9 syscall arguments from the emulated stack/registers into host Plan 9 libc calls.

Key elements:
- `sysctab[]` names supported syscall numbers from `/sys/src/libc/9syscall/sys.h`.
- `systab[]` maps syscall numbers to local handler functions.
- `Ssyscall()` reads the call number from `REGARG`, validates it, optionally traces, invokes the handler, and flushes output.
- Implemented syscalls include errstr/errstr variants, bind, fd2path, chdir, close, dup, exits, open, read/pread, seek/oseek, sleep, old/new stat and fstat, write/pwrite, pipe, create, brk, remove, and notify.
- Many syscalls are hard stubs that print “No system call” and exit: wait/await, rfork, wstat/fwstat, noted, segattach/detach/free/flush, rendezvous, unmount, fork/forkpgrp, segbrk, mount, alarm, exec, fsession, fauth, fversion.

Dependencies and integration:
- Uses guest memory helpers `getmem_w()`, `getmem_v()`, `putmem_w()`, `putmem_v()`, and `memio()`.
- Updates `reg.r[REGRET]` with syscall return values.
- Uses interpreter memory segment metadata for `sysbrk_()`.

Notable behavior:
- `sysread()` special-cases guest fd 0, reading from `bin` after printing a `stdin>>` prompt; other reads use `pread()`.
- `syswrite()` reads guest memory into a temporary host buffer before `pwrite()`.
- `sysbrk_()` grows the emulated BSS segment table and enforces data/stack bounds.
- Error text is stored in global `errbuf` and returned through errstr handlers.
- `sysfd2path()` appears suspicious: after successful `fd2path()`, it writes from `errbuf` to guest memory rather than the local `buf` that received the path.

Research notes:
- This is a pragmatic syscall subset, not a full Plan 9 process model.
- Unimplemented calls terminate the interpreter instead of returning `ENOSYS`.
