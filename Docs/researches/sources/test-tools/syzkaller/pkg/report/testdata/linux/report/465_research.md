# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/465

Purpose: golden fixture for RCU stall parsing where the interrupted top frame is lockdep. Expected title is `INFO: rcu detected stall in lock_is_held_type`, alternate title is `stall in lock_is_held_type`, and type is `HANG`.

Important APIs, types, and functions: parser coverage includes RCU stall matching and accepting lockdep helper frames as the expected title when they are the interrupted RIP. Kernel frames include `lock_is_held_type`, `rcu_read_lock_held`, `nfnetlink_rcv_msg`, `netlink_rcv_skb`, `nfnetlink_rcv`, `netlink_unicast`, `netlink_sendmsg`, and `__sys_sendmsg`.

Control flow: an RCU sched stall interrupts CPU 1 in `lock_is_held_type` while processing nfnetlink sendmsg. Unlike the previous nftables fixture, the expected title is the lockdep frame itself, so parser ranking must not always skip lock helpers for RCU stalls.

State and persistence behavior: static non-panicking stall fixture. It persists CPU/jiffies RCU stall counters, interrupted register state, and netlink receive stack.

Dependencies and integration points: depends on RCU stall parser rules, IRQ/timer frame stripping, and nuanced guilty-frame selection. Integrates lockdep/RCU state checking inside nfnetlink message processing.

Risks: overly aggressive helper filtering could skip `lock_is_held_type` and title the report as `nfnetlink_rcv_msg`; overly shallow parsing could lose netlink context. The fixture locks in the current expected balance.

Test signals: `rcu_sched self-detected stall on CPU`, `RIP: lock_is_held_type+0x1ca/0x240`, `rcu_read_lock_held`, `nfnetlink_rcv_msg`, and sendmsg syscall frames.
