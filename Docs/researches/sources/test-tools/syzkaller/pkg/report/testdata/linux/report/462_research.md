# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/462

Purpose: golden fixture for RCU stall parsing in ipset add handling. Expected title is `INFO: rcu detected stall in ip_set_uadd`, alternate title is `stall in ip_set_uadd`, and type is `HANG`.

Important APIs, types, and functions: parser behavior includes RCU stall recognition and user-context stack title extraction. Kernel frames include `hash_ipportnet4_expire`, `hash_ipportnet4_add`, `hash_ipportnet4_uadt`, `call_ad`, `ip_set_ad.isra.28`, `ip_set_uadd`, `nfnetlink_rcv_msg`, `netlink_rcv_skb`, `nfnetlink_rcv`, `netlink_unicast`, and `netlink_sendmsg`.

Control flow: an RCU preempt self-detected stall on CPU 3 triggers NMI backtrace output. After IRQ/timer frames, the interrupted code is an ipset hash expiration/add path reached through nfnetlink sendmsg. The parser must identify `ip_set_uadd` as the semantic stalled operation.

State and persistence behavior: static non-panicking stall fixture. It persists RCU generation/jiffies details and the interrupted stack.

Dependencies and integration points: depends on RCU stall oops matching, IRQ frame handling, and stack frame ranking across netfilter/ipset functions. Integrates ipset netlink add behavior into parser tests.

Risks: the current RIP is `hash_ipportnet4_expire`, while the expected title is the higher-level operation `ip_set_uadd`; parser heuristics must preserve that call-chain judgment.

Test signals: `rcu_preempt self-detected stall on CPU`, NMI backtrace, `hash_ipportnet4_expire`, `hash_ipportnet4_add`, `ip_set_uadd`, and netlink sendmsg syscall frames.
