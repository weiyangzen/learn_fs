# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/464

Purpose: golden fixture for RCU stall parsing in nftables generation query handling. Expected title is `INFO: rcu detected stall in nf_tables_getgen`, alternate title is `stall in nf_tables_getgen`, and type is `HANG`.

Important APIs, types, and functions: parser behavior includes RCU stall detection and selection of netfilter control-plane frames. Kernel frames include `check_memory_region`, `rcu_is_watching`, `rcu_read_lock_held_common`, `rcu_read_lock_held`, `netlink_lookup`, `netlink_unicast`, `nf_tables_getgen`, `nfnetlink_rcv_msg`, `nfnetlink_rcv`, and `netlink_sendmsg`.

Control flow: the RCU stall report starts with timer/NMI backtrace frames, then lands in KASAN memory checking and RCU lock-state helpers before the netlink/nftables call path. The parser must skip low-level instrumentation and choose `nf_tables_getgen`.

State and persistence behavior: static non-panicking hang fixture. It persists the interrupted CPU state and netlink syscall context.

Dependencies and integration points: depends on RCU stall parsing, KASAN/helper frame filtering, and nftables/netlink stack ranking. Integrates nftables generation queries into syzkaller report coverage.

Risks: instrumentation frames such as `check_memory_region` and RCU lock helpers are noisy and could produce poor titles. The expected title relies on deeper stack inspection.

Test signals: `rcu_sched self-detected stall on CPU`, `RIP: check_memory_region`, frames `rcu_read_lock_held -> netlink_lookup -> netlink_unicast -> nf_tables_getgen`, and netlink sendmsg syscall context.
