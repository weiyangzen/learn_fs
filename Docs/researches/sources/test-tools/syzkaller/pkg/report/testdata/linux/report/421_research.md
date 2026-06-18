# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/421

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: rcu detected stall in sys_exit_group`, alternates for `__x64_sys_exit_group` and stall wording, type `HANG`, corrupted `N`, panicked `N`. The log covers an RCU preempt self-detected stall with NMI backtraces and network softirq activity.

Important APIs, types, and functions: this tests RCU stall title extraction and alternate generation. Key frames include `rcu_gp_kthread`, `hhf_dequeue`, `__qdisc_run`, bridge forwarding, IGMP timer paths, `_raw_write_unlock_irq`, `do_exit`, `do_group_exit`, and `__x64_sys_exit_group`.

Control flow: 261 log lines are parsed. The reporter must recognize the RCU stall headline, inspect NMI/user task stacks, and choose the syscall exit path as the title while preserving alternates.

State and persistence behavior: expected alternates are persisted in headers; runtime state is crash span, stack scanning state, and flags.

Dependencies, integration points, risks, and test signals: this protects hang grouping for RCU stall reports with noisy multi-CPU stacks. Risks include selecting softirq bridge frames or RCU kthread helpers. Passing tests require HANG type, all alternates, no panic, and no corruption.
