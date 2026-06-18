# File Research: sources/os/bsd/freebsd-src/sys/sys/thr.h

## Scope

This header defines the low-level FreeBSD thread syscall user ABI, including thread creation flags, `struct thr_param`, and userland prototypes for the `thr_*` system call wrappers.

## APIs And Constants

- Defines thread creation flags `THR_SUSPENDED`, `THR_SYSTEM_SCOPE`, and `THR_C_RUNTIME`.
- Defines `struct thr_param` with entry function, argument, stack base/size, TLS base/size, child and parent TID pointers, flags, realtime priority pointer, and spare slots.
- Ensures `size_t` is declared from `<sys/_types.h>`.
- Outside `_KERNEL`, includes `<sys/ucontext.h>`, ensures `pid_t` is declared, and declares `thr_create()`, `thr_new()`, `thr_self()`, `thr_exit()`, `thr_kill()`, `thr_kill2()`, `thr_suspend()`, `thr_wake()`, and `thr_set_name()`.

## Control Flow And Integration

- `thr_new()` uses `struct thr_param` as an extensible syscall argument block whose `param_size` is passed separately in `sysproto.h`.
- `thr_create()` takes a full user context, while `thr_new()` takes explicit stack/TLS/entry fields.
- Child and parent TID pointers provide user-visible synchronization points for thread creation and exit.
- The realtime priority pointer allows thread creation with scheduling attributes.

## Dependencies

- Includes C declaration macros, internal type definitions, and scheduler priority structures.
- Userland prototypes depend on `ucontext_t`, `pid_t`, and `struct timespec`.
- Tied to generated syscall argument declarations in `sysproto.h` for `thr_create`, `thr_new`, and related thread syscalls.

## Risks And Invariants

- `struct thr_param` is a user/kernel ABI structure; field order and sizes are compatibility-sensitive.
- `param_size` must be validated by syscall code before reading optional or future fields.
- TID pointer handling crosses user/kernel memory boundaries and must be copied or written carefully by implementations.
- The spare fields are reserved for future ABI extension and should not be repurposed casually.
