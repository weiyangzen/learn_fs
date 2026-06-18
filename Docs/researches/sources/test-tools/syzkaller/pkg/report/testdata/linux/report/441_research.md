# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/441

Purpose: golden fixture for Linux hung-task parsing where the canonical title is `INFO: task hung in rtnl_lock`, alternate title is `hang in rtnl_lock`, and crash type is `HANG`.

Important APIs, types, and functions: the fixture is consumed by `report_test.go` through `ParseTest`, `parseReport`, `parseHeaderLine`, `Reporter.Parse`, `Reporter.ContainsCrash`, and `crash.TitleToType`. The kernel stack exercises `rtnl_lock`, `ipv6_sock_ac_close`, `inet6_release`, `__sock_release`, `sock_close`, `__fput`, `task_work_run`, and exit-to-usermode paths. It also includes many lock inventory lines for `rtnl_mutex`, `pernet_ops_rwsem`, workqueue completions, and socket inode mutexes.

Control flow: the test reader first parses the three expectation headers, then feeds the full hung-task log to the Linux reporter. The log begins with a blocked `syz-executor.1` task, walks through scheduler and mutex acquisition frames into the IPv6 socket close path, prints all locks held in the system, and later includes additional blocked executor evidence. Parser control flow must choose the original hung-task report, retain `rtnl_lock` as the title frame, and avoid treating lock inventory or repeated blocked tasks as separate higher-priority reports.

State and persistence behavior: this is static testdata with no runtime mutation. The meaningful persisted state is the expected title, alternate title, and `HANG` type plus the raw console stream that preserves long lock-list ordering.

Dependencies and integration points: depends on Linux hung-task regexes in the report package, console-prefix stripping in the Linux reporter, and the test harness' convention that blank line separates headers from log. It integrates with syzkaller's report parser regression suite and protects parsing of network namespace/socket lock hangs.

Risks: the long file stresses parser boundaries because it contains many `rtnl_mutex` holders, repeated executor PIDs, workqueue stacks, and lock debug output. A too-greedy parser may select a later lock owner or emit a generic scheduler title instead of `rtnl_lock`.

Test signals: `INFO: task syz-executor.1:5269 blocked for more than 140 seconds`, stack frame `rtnl_lock+0x17/0x20`, IPv6 close frames, `Showing all locks held in the system`, and repeated `rtnetlink_rcv_msg`/workqueue holders of `rtnl_mutex`.
