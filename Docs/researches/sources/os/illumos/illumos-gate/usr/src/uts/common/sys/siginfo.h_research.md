# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/siginfo.h

## Role

Defines signal information ABI structures, signal codes, queued-signal kernel structures, and 32-bit translation interfaces.

## Key Interfaces

- Defines `union sigval`, kernel ILP32 `sigval32`, `struct sigevent`, `sigevent32`, and `SIGEV_*` notification modes.
- Signal-origin macros: `SI_FROMUSER()` and `SI_FROMKERNEL()`.
- Signal codes include `SI_NOINFO`, `SI_DTRACE`, `SI_RCTL`, `SI_USER`, `SI_LWP`, `SI_QUEUE`, `SI_TIMER`, `SI_ASYNCIO`, and `SI_MESGQ`.
- Pulls machine-dependent codes from `machsig.h` and defines trap, child, poll, and profile codes.
- `siginfo_t` is the padded public ABI with process, fault, file, profiling, and rctl unions.
- `siginfo32_t` is the kernel view of ILP32 `siginfo_t`.
- `k_siginfo_t` is the smaller internal version without public padding.
- `sigqueue_t` stores queued signal info plus destructor/backpointer metadata.
- Field aliases expose `si_pid`, `si_addr`, `si_value`, `si_status`, `si_entity`, and related members.
- `_SYSCALL32_IMPL` declares `siginfo_kto32()` and `siginfo_32tok()`.

## Risk Notes

Public padding sizes differ between LP64 and ILP32 and are ABI-fixed. `k_siginfo_t` must remain semantically synchronized with `siginfo_t` while intentionally omitting bulk padding.
