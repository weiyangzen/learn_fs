# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/611

## Purpose
This fixture is a sibling RCU self-stall hang for `sys_sendmmsg`. It verifies that the parser can distinguish sendmmsg from nearby scheduler and migration frames.

## Important APIs, types, and functions
Important symbols include `rcu_sched_clock_irq`, `nmi_trigger_cpumask_backtrace`, `lock_is_held_type`, `rcu_read_lock_sched_held`, `lock_acquire`, `_raw_spin_lock`, `__migration_entry_wait`, and the expected syscall aliases `sys_sendmmsg` and `__x64_sys_sendmmsg`.

## Control flow
An RCU stall on CPU 1 produces an RCU kthread dump and an NMI backtrace. The useful stack descends through lock/migration waiting in the sendmmsg syscall context.

## State and persistence behavior
The file has no runtime state. It persists the expected hang classification and alternate titles for parser regression checks.

## Dependencies and integration points
It targets syzkaller's Linux RCU stall extractor and syscall alias matching.

## Risks and test signals
The risk is taking helper frames such as `lock_acquire` as the report identity. The test signal is the primary title ending in `sys_sendmmsg`.
