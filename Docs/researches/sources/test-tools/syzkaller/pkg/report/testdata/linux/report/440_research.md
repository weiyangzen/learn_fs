# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/440

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in rtnl_lock`, alternate `hang in rtnl_lock`, type `HANG`, corrupted `N`, panicked `Y`. The report covers TIPC network namespace exit blocked on RTNL.

Important APIs, types, and functions: this tests hung-task selection for network teardown lock contention. Key frames include `__mutex_lock`, `mutex_lock_nested`, `rtnl_lock`, `tipc_net_stop`, `tipc_exit_net`, `ops_exit_list.isra.0`, `cleanup_net`, and workqueue helpers.

Control flow: 260 log lines are parsed. The first blocked task stack identifies RTNL lock acquisition; long tail output and additional diagnostic stacks should not change the expected title.

State and persistence behavior: expected title/type/panic are stored in fixture headers; parser runtime state is temporary.

Dependencies, integration points, risks, and test signals: this pairs with report 436 to protect RTNL lock hang deduplication across IPv6 and TIPC callers. Risks include selecting caller-specific `tipc_net_stop` or generic mutex helpers. Passing tests require the RTNL hang title/alternate, HANG type, panic `Y`, and no corruption.
