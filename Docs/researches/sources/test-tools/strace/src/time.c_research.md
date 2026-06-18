# sources/test-tools/strace/src/time.c

Purpose: decoders for time, timer, clock, nanosleep, adjtimex, and timerfd syscalls across time32/time64 and special architectures.

Important APIs/types/functions: `print_timezone`, `do_nanosleep`, `do_adjtimex`, `printclockname`, `do_clock_settime`, `do_clock_gettime`, `do_clock_nanosleep`, `do_clock_adjtime`, `timer_create`, `timer_delete`, `do_timer_settime`, `do_timer_gettime`, `timerfd_create`, `do_timerfd_settime`, and `do_timerfd_gettime`.

Control flow: setter calls print input structures on entry and return `RVAL_DECODED`; getter calls usually print scalar selectors on entry and output structures on exit. Sleep decoders print remaining time only when syscall is interrupted/restartable and temporarily clear syscall error so output structures can be fetched. `printclockname` handles ordinary clocks plus negative FD/cpu clock encodings when supported. Adjtimex decoders attach state text through `tcp->auxstr`.

State and persistence behavior: no persistent module state; temporarily uses `tcp->auxstr` and the syscall error-clear helpers from `syscall.c`.

Dependencies and integration points: depends on time structure printers, `kernel_fcntl.h`, signal event printing, timex xlats, clock/timer flag xlats, and syscall table variants for time32/time64/Alpha/SPARC.

Risks: output buffers must be decoded only when the kernel writes them. Restart errno handling is subtle for nanosleep and clock_nanosleep. Negative clock IDs encode multiple namespaces and need correct bit macros.

Test signals: get/settimeofday, nanosleep interrupted vs success, get/setitimer, adjtimex return strings, clock get/set/adjtime, CPU and fd clock IDs, absolute vs relative clock_nanosleep, timer create/delete/set/get, timerfd create/set/get, time32/time64 variants, and Alpha/SPARC special printers.
