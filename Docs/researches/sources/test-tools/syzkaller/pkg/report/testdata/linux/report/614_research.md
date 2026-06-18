# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/614

## Purpose
This long fixture validates a panicking kernel stack overflow in `rtnl_newlink`, with alternate title `stack-overflow in rtnl_newlink`.

## Important APIs, types, and functions
Key frames include `netdev_next_lower_dev_rcu`, `bond_get_lowest_level_rcu`, `bond_get_stats`, `dev_get_stats`, `rtnl_fill_stats`, `rtnl_fill_ifinfo`, `rtmsg_ifinfo_build_skb`, `rtnetlink_event`, `netdev_change_features`, `bond_compute_features`, `bond_netdev_event`, `bond_option_xmit_hash_policy_set`, `bond_changelink`, `__rtnl_newlink`, `rtnl_newlink`, and `netlink_sendmsg`.

## Control flow
A netlink `sendmsg` creates or changes a bonding device through rtnetlink. Bond feature updates recursively notify network-device listeners, repeatedly re-entering feature recomputation until the stack guard page is hit and the kernel panics.

## State and persistence behavior
The fixture stores the panic marker and an intentionally repetitive stack. The persistence concern is parser stability across deep recursion, not mutable program state.

## Dependencies and integration points
It exercises stack-overflow detection, panic recognition, network-device notifier recursion, rtnetlink syscall attribution, and report deduplication for repeated frames.

## Risks and test signals
The risk is selecting the top faulting helper `netdev_next_lower_dev_rcu` instead of the actionable entry point. Passing behavior preserves `BUG: stack guard page was hit in rtnl_newlink` and `PANICKED: Y`.
