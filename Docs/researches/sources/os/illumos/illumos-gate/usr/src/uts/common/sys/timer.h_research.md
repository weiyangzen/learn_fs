# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timer.h

## Purpose
Kernel timer implementation header for per-process POSIX timers, clock backends, old sigevent compatibility, and timespec helper routines.

## Main Interfaces
- Defines `_TIMER_MAX` and `_TIMER_ALLOC_INIT` for per-process timer arrays.
- Defines interval timer lock flags `ITLK_LOCKED`, `ITLK_WANTED`, and `ITLK_REMOVE`.
- Defines notification flags `IT_SIGNAL` and `IT_PORT`.
- Defines `itimer_t`, `struct itimer`, and `clock_backend_t`.
- `struct itimer` carries timer ID, process/LWP links, lock state, overrun accounting, sigevent data, backend pointer, and fire callback.
- `clock_backend_t` provides clock and timer method vectors for set/get/resolution/create/settime/gettime/delete/LWP binding.
- Declares backend registration and timer routines such as `clock_add_backend`, `clock_get_backend`, `timer_exit`, `timer_lwpexit`, `hzto`, `timespectohz`, `itimerspecfix`, `timespecadd`, `timespecsub`, and `xgetitimer`/`xsetitimer`.
- Defines `struct oldsigevent` and `struct oldsigevent32` for compatibility.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/proc.h`, `sys/thread.h`, and `sys/param.h`. It is consumed by kernel timer, signal, event port, and clock backend code.

## Research Notes
The design separates generic POSIX timer state from pluggable clock backend operations, allowing different clock IDs to supply their own implementation while sharing process timer bookkeeping.
