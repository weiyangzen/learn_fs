# File Research: sources/os/bsd/netbsd-src/sys/kern/syscalls.c

Generated syscall-name table from `syscalls.master`, produced by `makesyscalls.sh`. It should not be edited manually.

Contents:
- `syscallnames[]`: canonical syscall names indexed by syscall number, from 0 through 511.
- `altsyscallnames[]`: optional libc-style alternate names for selected syscall numbers, otherwise `NULL`.

Notable coverage in this group:
- Scheduler syscalls are named at 346-351: `_sched_setparam`, `_sched_getparam`, `_sched_setaffinity`, `_sched_getaffinity`, `sched_yield`, `_sched_protect`.
- Select/poll modern names include `__select50`, `__pselect50`, `__pollts50`, plus legacy compat entries.
- Signal entries include `__sigaction_sigtramp`, `__sigpending14`, `__sigprocmask14`, `__sigsuspend14`, `____sigtimedwait50`, `sigqueueinfo`, `getcontext`, and `setcontext`.
- Socket table names include classic socket calls and `__socket30`.
- Timerfd names are 177-179: `timerfd_create`, `timerfd_settime`, `timerfd_gettime`.

Conditional generation:
- Includes conditional names for options like `_LP64`, `NTP`, and `_KERNEL_OPT`.
- Uses generated comments for obsolete, excluded, filler, and unimplemented syscall slots.

Research notes:
- This file contains no dispatch implementation; it is metadata used for names, tracing, diagnostics, and generated syscall infrastructure.
