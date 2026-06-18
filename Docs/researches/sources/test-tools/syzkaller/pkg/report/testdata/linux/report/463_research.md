# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/463

Purpose: golden fixture for RCU stall parsing in generic ipset add/delete handling. Expected title is `INFO: rcu detected stall in ip_set_ad`, alternate title is `stall in ip_set_ad`, and type is `HANG`.

Important APIs, types, and functions: parser coverage includes RCU stall detection and title selection from netfilter/ipset call chains. Kernel frames include `hash_ip4_expire.isra.17`, `hash_ip4_add`, `hash_ip4_uadt`, `call_ad`, `ip_set_ad.isra.33`, `nfnetlink_rcv_msg`, `nfnetlink_rcv`, `netlink_unicast`, and `netlink_sendmsg`.

Control flow: the CPU self-detected RCU stall interrupts an ipset hash operation. The report moves from timer/RCU backtrace frames to the network set update path and then to a userspace `sendmsg`. The parser should report the higher-level `ip_set_ad` operation.

State and persistence behavior: static stall fixture with no panic. It persists older prefix formatting without `[T...]` contexts on every line.

Dependencies and integration points: depends on Linux RCU stall matchers, IRQ boundary stripping, and netfilter frame ranking. Integrates ipset hash4 add/update paths into the parser suite.

Risks: top interrupted frame `hash_ip4_expire` could be chosen if the parser does not climb the stack. `ip_set_ad.isra.33` suffix normalization should still match the expected title.

Test signals: `rcu_sched self-detected stall on CPU`, `hash_ip4_expire.isra.17`, `hash_ip4_add`, `ip_set_ad.isra.33`, `nfnetlink_rcv_msg`, and `sendmsg` syscall frames.
