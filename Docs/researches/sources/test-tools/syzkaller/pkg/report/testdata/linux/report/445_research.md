# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/445

Purpose: golden fixture for a multi-task hang where the canonical title is `INFO: task hung in synchronize_rcu`, alternates include `synchronize_rcu_expedited`, and type is `HANG`.

Important APIs, types, and functions: parser APIs are fixture headers, `Reporter.Parse`, and title-to-type mapping. Kernel frames include `synchronize_rcu_expedited`, `synchronize_net`, `rollback_registered_many`, `unregister_netdevice_many`, `vti6_exit_batch_net`, `cleanup_net`, and many `rtnl_lock` waiters in `dev_ioctl` and `rtnetlink_rcv_msg`.

Control flow: a netns cleanup worker blocks in an expedited RCU grace period while syz-executor tasks block on RTNL-related ioctls and netlink requests. The parser must select the RCU synchronization hang from the first blocked task, generate alternate names, and keep later RTNL waiters as context.

State and persistence behavior: static data persists modern `[ T...]` task context prefixes and the full lock list. It has no `PANICKED` header, so panic detection should remain false.

Dependencies and integration points: depends on Linux console context stripping, hung-task start detection, alternate-title derivation, and network cleanup stack handling. Integrates vti6 namespace teardown and RTNL lock contention into the test suite.

Risks: there are many plausible blocking frames. A parser that reports the most frequent waiter would produce `rtnl_lock`; the expected result requires prioritizing the first reported hung task and mapping expedited RCU to the canonical synchronize-rcu title.

Test signals: blocked `kworker/u4:0` in `netns cleanup_net`, `synchronize_rcu_expedited+0x57f/0x5f0`, `rollback_registered_many`, several executor `dev_ioctl` stacks, and lock inventory for blocked tasks.
