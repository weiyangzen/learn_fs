<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/272 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/272

## Purpose
This fixture verifies RCU stall parsing for a netlink send path involving TIPC compatibility dumps. The expected title is `INFO: rcu detected stall in netlink_sendmsg`, alt `stall in netlink_sendmsg`, and type `HANG`.

## Important APIs, Types, and Functions
The raw log is an `rcu_sched self-detected stall on CPU`. Parser paths include RCU stall matching, NMI/IRQ frame skipping, and network-stack frame selection. Important symbols include `lock_acquire`, `tipc_sk_lookup`, `tipc_nl_publ_dump`, `__tipc_nl_compat_dumpit.isra.11`, `tipc_nl_compat_sk_dump`, `tipc_nl_compat_recv`, `genl_family_rcv_msg`, `netlink_rcv_skb`, `netlink_unicast`, `netlink_sendmsg`, `sock_sendmsg`, and `__x64_sys_sendmsg`.

## Control Flow
The reporter processes timer and RCU frames first, then the network stack. It should title at `netlink_sendmsg`, the user-facing send path, rather than deeper TIPC dump helpers.

## State and Persistence Behavior
No mutable state exists. The fixture stores expected HANG metadata and raw log text.

## Dependencies and Integration Points
It depends on RCU stall patterns, stack parser ordering, and hang title normalization.

## Risks and Edge Cases
Many deeper TIPC functions appear before `netlink_sendmsg`; parser heuristics must still produce the expected stable subsystem boundary.

## Test Signals
The parse must produce `INFO: rcu detected stall in netlink_sendmsg`, alt `stall in netlink_sendmsg`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/272 -->
