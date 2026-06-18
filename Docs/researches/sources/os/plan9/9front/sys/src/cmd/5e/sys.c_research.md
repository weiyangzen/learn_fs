# File Research: sources/os/plan9/9front/sys/src/cmd/5e/sys.c

This file translates emulated Plan 9 ARM syscalls into host Plan 9 syscalls.

Argument handling:
- `arg(n)` reads 32-bit syscall arguments from the emulated stack.
- `argv(n)` combines two 32-bit words into a 64-bit argument.
- Syscall return values are written to `P->R[0]`.
- `noteerr()` is used to capture host error strings into `P->errbuf`.

Implemented syscalls:
- File operations: `open`, `create`, `close`, `pread`, `pwrite`, `seek`, `fd2path`, `stat`, `fstat`, `wstat`, `fwstat`, `remove`.
- Process/control: `exits`, `brk`, `errstr`, `chdir`, `notify`, `noted`, `rfork`, `exec`, `await`, `sleep`, `rendezvous`, `alarm`.
- Namespace/mount: `bind`, `mount`, `unmount`, `fauth`.
- IPC/fd: `pipe`, `dup`.
- Synchronization: `semacquire`, `semrelease`.

Memory marshalling:
- String and read-only buffers use `copyifnec()` when memory may be lock-protected.
- Output buffers use `bufifnec()` and `copyback()` for safe mutation.
- `sysbrk()` resizes the BSS segment under write lock, zero-filling new memory.
- `sysexec()` copies the emulated argv vector and strings into host memory before calling `loadtext()`.

`rfork()` behavior:
- Validates mutually exclusive flag combinations.
- For non-`RFPROC`, updates fd-table sharing/clearing then calls host `rfork()`.
- For `RFPROC`, allocates a copied `Process`, duplicates or shares segments according to flags, handles fd table sharing/copy/clear, forks with `RFMEM|flags`, installs child `P`, updates pid/Tos, and adds to process list.

Dispatcher:
- `syscall()` uses `P->R[0]` as the syscall number and dispatches through a static function table included from Plan 9 syscall numbers.

Dependencies and interactions:
- Called by `arm.c` on SWI/syscall instructions.
- Uses memory helpers from `seg.c`, process loading from `proc.c`, fd helpers, and Plan 9 syscall constants.

Research relevance:
- This is the emulator’s OS compatibility layer.

Risk notes:
- Unsupported syscall numbers fatal the emulator.
- Syscall tracing is compile-time disabled unless `systrace` macro changes.
- `rfork()` state copying is complex and must keep segment/data refs, fd refs, path refs, process list, and thread-private `P` consistent.
