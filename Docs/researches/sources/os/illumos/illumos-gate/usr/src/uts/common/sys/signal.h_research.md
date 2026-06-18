# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/signal.h

## Role

Defines the main illumos signal ABI beyond ISO C: signal sets, `sigaction`, alt stacks, signotify, kernel masks, signal queueing, and signal-set helpers.

## Key Interfaces

- Includes ISO signal definitions and conditionally includes `siginfo.h`.
- Duplicates `sigset_t` for XPG compatibility and defines compact kernel `k_sigset_t`.
- `struct sigaction` stores flags, overlapped handler/sigaction function pointer, mask, and ILP32 reserved padding.
- `struct sigaction32` is the kernel view of ILP32 sigaction.
- Defines `SA_*` flags, `NSIG`, `MAXSIG`, stack sizes, `SS_*` flags, `stack_t`, and `stack32_t`.
- `signotify_id_t` and syscall command constants support libc notification for mqueue/aio.
- Kernel exports standard signal masks, bit macros, mask conversion helpers, `sigsend_t`, `signotifyq_t`, `sigqhdr_t`, queue-size limits, and signal-set manipulation functions.
- Kernel declares `kill()`.

## Compatibility Notes

Most definitions are guarded by standards namespace macros. `NSIG`/`MAXSIG` are exposed only where extensions or non-XPG constraints allow.

## Risk Notes

Signal masks assume `MAXSIG` fits three 32-bit kernel words. Changes to signal numbering or mask width require updates to fill/cannot-mask constants and user/kernel conversion macros.
