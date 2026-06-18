# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/610

## Purpose
This fixture validates an RCU self-stall hang attributed to `sys_recvmmsg` with alternates for `__x64_sys_recvmmsg` and shorter stall titles.

## Important APIs, types, and functions
Key frames include `rcu_sched_clock_irq`, `hrtimer_interrupt`, `copy_user_generic_unrolled`, `__copy_msghdr_from_user`, `___sys_recvmsg`, `do_recvmmsg`, `__x64_sys_recvmmsg`, `do_syscall_64`, and `entry_SYSCALL_64_after_hwframe`.

## Control flow
The log first dumps the RCU grace-period kthread, then an NMI backtrace for CPU 0, and finally shows the interrupted syscall path copying a user msghdr for recvmmsg.

## State and persistence behavior
The file is immutable parser data. Its meaningful persisted state is the expected primary and alternate titles plus `TYPE: HANG`.

## Dependencies and integration points
It exercises integration between the report parser, RCU stall format handling, interrupt/NMI trace parsing, and syscall-name normalization.

## Risks and test signals
The parser must find the syscall frame despite timer and RCU frames. Passing output is the exact title `INFO: rcu detected stall in sys_recvmmsg`.
