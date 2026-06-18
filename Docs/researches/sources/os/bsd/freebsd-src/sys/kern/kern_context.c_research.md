# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_context.c

## Purpose
Implements the `getcontext(2)`, `setcontext(2)`, and `swapcontext(2)` system calls for saving and restoring user execution context and signal masks.

## Main Elements
- `UC_COPY_SIZE` copies only the signal mask and machine context portion of `ucontext_t`, intentionally avoiding `uc_link`.
- `sys_getcontext()` validates the user pointer, clears a kernel `ucontext_t`, fills machine context with `get_mcontext(..., GET_MC_CLEAR_RET)`, copies the thread signal mask under `PROC_LOCK`, and copies the result out.
- `sys_setcontext()` copies in context data, applies machine state with `set_mcontext()`, updates the signal mask with `kern_sigprocmask()`, and returns `EJUSTRETURN` on success.
- `sys_swapcontext()` saves the current context to `oucp`, then loads the new context from `ucp`, returning `EJUSTRETURN` on success.

## Dependencies And Integration
Relies on MD `get_mcontext()` and `set_mcontext()`, process signal-mask locking, `copyin()`/`copyout()`, syscall argument structures, and `kern_sigprocmask()`.

## Risk Notes
The implementation is small but ABI-sensitive. `UC_COPY_SIZE` protects `uc_link` from accidental overwrite during kernel/user transfers. Success returns `EJUSTRETURN`, so callers resume through the restored machine context rather than normal syscall return.
