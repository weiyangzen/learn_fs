# sources/test-tools/strace/src/linux/32/syscallent-time32.h

## Purpose

`sources/test-tools/strace/src/linux/32/syscallent-time32.h` overrides legacy 32-bit syscall table slots whose ABI passes 32-bit time-related structures. It maps old syscall names such as `ppoll`, `utimensat`, `clock_gettime`, and `futex` to explicit `*_time32` decoders while preserving the user-visible syscall names.

The file is included only when `HAVE_ARCH_TIME32_SYSCALLS` is true. It keeps old 32-bit syscall decoding separate from the newer time64 rows in `syscallent-common-32.h`.

## Important APIs, Types, And Data Shape

The file emits indexed `struct_sysent` initializer rows for legacy syscall numbers. Each row uses the standard strace table shape: argument count, trace flags, `SEN(decoder)`, and printable syscall name.

Covered groups include AIO and polling (`io_getevents_time32`, `pselect6_time32`, `ppoll_time32`, `io_pgetevents_time32`), timer and clock syscalls (`timerfd_*time32`, `timer_*time32`, `clock_*time32`, `nanosleep_time32`, `sched_rr_get_interval_time32`), filesystem timestamp updates (`utimensat_time32`), futex and signal waits (`futex_time32`, `rt_sigtimedwait_time32`), message queues (`mq_timedsend_time32`, `mq_timedreceive_time32`), SysV semaphores (`semtimedop_time32`), networking (`recvmmsg_time32`), and legacy time-of-day/timex calls (`gettimeofday`, `settimeofday`, `adjtimex32`).

Rows preserve trace flags such as `TD`, `TF`, `TCL`, `TN`, `TI`, `TS`, and `TP` so filtering and classification remain consistent with the base syscall table.

## Control Flow

There is no executable control flow in this file. The inclusion flow is conditional: `src/linux/32/syscallent.h` includes it under `#if HAVE_ARCH_TIME32_SYSCALLS` before including `syscallent-common-32.h` and `syscallent-common.h`. The entries replace commented placeholder slots in the base table, for example clock/timer/poll/futex slots that would otherwise be generic comments or architecture-specific rows.

At runtime, the compiled syscall table directs legacy syscall numbers to time32-specific decoders. Newer time64 syscall numbers are handled separately by `syscallent-common-32.h`.

## State And Persistence Behavior

The file has no mutable state, allocation, I/O, or persistence. Its effect is compiled read-only syscall table state. Runtime persistence is limited to the process-wide selected `sysent` pointer/count in multi-personality builds.

## Dependencies

Dependencies are `HAVE_ARCH_TIME32_SYSCALLS` from `arch_defs.h` or architecture overrides, `SEN` decoder declarations for all listed time32 handlers, the corresponding decoder implementations in files such as `time.c`, `poll.c`, `futex.c`, `mmsghdr.c`, `mq.c`, `ipc_sem.c`, `aio.c`, `signal.c`, `sched.c`, `utimes.c`, and `wait.c`, plus trace flag definitions used by syscall filtering and reporting.

## Integration Points

This fragment integrates with the shared 32-bit syscall table and with architecture-specific 32-bit syscall tables that reuse it. It is the legacy counterpart to `syscallent-common-32.h`: old syscall numbers keep names like `clock_gettime` and `futex` but use time32 decoding, while added y2038-safe syscall numbers carry explicit `*_time64` names and decoders.

## Risks

The central risk is mixing time32 and time64 decoders. A wrong decoder would read timeout, timespec, timeval, or timex arguments with the wrong layout and produce bad output or memory reads. Conditional inclusion must match architecture reality; enabling it for a no-time32 ABI or disabling it for a legacy 32-bit ABI would misdecode many common syscalls. Trace flag drift is also risky because these rows affect `-e trace=` classes, path/fd handling, and syscall summaries.

## Test Signals

Useful signals are 32-bit builds with `HAVE_ARCH_TIME32_SYSCALLS=1`, decoder tests for representative legacy calls such as `clock_gettime`, `ppoll`, `utimensat`, `futex`, `recvmmsg`, and `semtimedop`, y2038 boundary fixtures showing 32-bit time fields decoded as time32, and paired tests confirming that `clock_gettime64`/`futex_time64` use the separate time64 entries rather than these legacy rows.
