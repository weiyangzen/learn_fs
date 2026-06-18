# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/615

## Purpose
This is another panicking `rtnl_newlink` stack-overflow fixture, but the top frame is `arch_stack_walk`, making it a stronger test of frame filtering.

## Important APIs, types, and functions
Important symbols include `arch_stack_walk`, `stack_trace_save`, KASAN stack tracking helpers, `pskb_expand_head`, `netlink_trim`, `netlink_broadcast_filtered`, `nlmsg_notify`, `rtnetlink_event`, `bond_netdev_event`, `bond_compute_features`, `br_add_if`, `do_set_master`, `__rtnl_newlink`, `rtnl_newlink`, and `netlink_sendmsg`.

## Control flow
The log shows bonding and bridge-related feature updates recursing through netdevice notifier chains during a rtnetlink newlink operation. Stack tracing and KASAN allocation tracking appear near the top because the overflow interrupts instrumentation.

## State and persistence behavior
The file persists `PANICKED: Y` and repeated recursive frames. It has no runtime persistence outside the test fixture.

## Dependencies and integration points
It integrates stack-overflow parsing with bridge, bonding, ethtool notification, netlink broadcast, and kernel instrumentation noise.

## Risks and test signals
The parser must not title the crash after `arch_stack_walk` or KASAN helpers. The expected stable signal is `stack-overflow in rtnl_newlink`.
