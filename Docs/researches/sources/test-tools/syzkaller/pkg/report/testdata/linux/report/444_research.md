# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/444

Purpose: compact golden fixture for a network namespace cleanup worker hung on `rtnl_lock`. Expected title is `INFO: task hung in rtnl_lock`, alternate title is `hang in rtnl_lock`, and type is `HANG`.

Important APIs, types, and functions: parser-facing types are the standard report fixture headers. Kernel frames are `rtnl_lock`, `nat_exit_net`, `ops_exit_list.isra.0`, `cleanup_net`, `process_one_work`, `worker_thread`, `kthread`, and `ret_from_fork`.

Control flow: the log contains a single blocked `kworker/u4:0` on the `netns cleanup_net` workqueue. The reporter strips prefixes, sees the hung-task banner, follows the call trace to the first non-scheduler blocking frame, and emits `rtnl_lock`.

State and persistence behavior: no runtime state is created; the file persists a minimal netns cleanup hang to keep parser behavior stable for short reports.

Dependencies and integration points: depends on hung-task matching, workqueue context parsing, and title selection for kernel worker tasks rather than syz-executor processes. Integrates netfilter NAT namespace teardown into Linux report tests.

Risks: because the fixture is short, over-filtering scheduler/mutex frames must still leave enough signal to title the report. Worker task names should not be required to contain `syz-executor`.

Test signals: `Workqueue: netns cleanup_net`, `rtnl_lock+0x17/0x20`, `nat_exit_net+0x25/0x380`, and `cleanup_net+0x4d8/0xa20`.
