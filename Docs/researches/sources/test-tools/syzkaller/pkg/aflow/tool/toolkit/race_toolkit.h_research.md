# sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/race_toolkit.h

## Purpose
C header toolkit for race-condition reproducers, providing CPU pinning, barriers, futex events, monotonic timers, unbuffered I/O, and userfaultfd registration.

## Important APIs, Types, and Functions
Macros include `SETUP_UNBUFFERED_IO`, `PIN_TO_CPU`, `MB`, `WAIT_ON`, `SIGNAL`, `TIMER_START`, and `TIMER_NOT_EXPIRED`. Types/functions include `event_t`, `event_init`, `event_reset`, `event_set`, `event_wait`, `timer_elapsed_sec`, and `setup_uffd`.

## Control Flow
Spin waits use acquire loads until a value appears; signals use release stores. Futex events set state and wake waiters. Timers use `CLOCK_MONOTONIC`. `setup_uffd` creates nonblocking userfaultfd, negotiates API, and registers a missing-page range, closing on setup failures.

## State and Persistence Behavior
State is local process memory plus kernel resources such as futex waits and userfaultfd file descriptors. No persistent storage.

## Dependencies and Integration Points
Included by C reproducers via `get-toolkit`; depends on Linux headers, pthread/sched/futex/syscall/ioctl APIs.

## Risks and Test Signals
Risks include privilege-dependent userfaultfd, CPU affinity failures, busy-wait CPU burn, event double-set fatal exit, and timing sensitivity in VMs. C testdata compiles and exercises the main primitives.
