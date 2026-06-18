# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/629

## Purpose
This fixture covers a non-panicking stack guard hit in `rtnl_newlink` on a 5.16 kernel.

## Important APIs, types, and functions
Important frames include `mark_lock`, `__lock_acquire`, `psi_group_change`, `psi_task_switch`, `__schedule`, `ethnl_default_notify`, `ethtool_notify`, `ethnl_netdev_event`, `__netdev_update_features`, `bond_compute_features`, `bond_netdev_event`, and rtnetlink newlink handling.

## Control flow
Network-device feature updates recursively notify bonding and ethtool listeners. A timer interrupt and scheduler/lockdep path appear near the guard-page hit, but the deeper source is rtnetlink newlink recursion.

## State and persistence behavior
The file persists a long recursive trace and expected alternate title. It lacks `PANICKED: Y`, distinguishing it from reports 614 and 615.

## Dependencies and integration points
It integrates stack-overflow parsing with lockdep, PSI, ethtool netlink notifications, and bonding notifier recursion.

## Risks and test signals
The risk is titling the report as `mark_lock` or scheduler code. Passing behavior identifies `BUG: stack guard page was hit in rtnl_newlink`.
