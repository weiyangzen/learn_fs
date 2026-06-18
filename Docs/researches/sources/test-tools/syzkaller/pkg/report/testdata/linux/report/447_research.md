# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/447

Purpose: golden fixture for repeated 9p transport close hangs. Expected title is `INFO: task hung in p9_fd_close`, alternate title is `hang in p9_fd_close`, type is `HANG`, and `PANICKED: Y`.

Important APIs, types, and functions: report parser interfaces are the same fixture and `Reporter.Parse` path. Kernel frames include `wait_for_completion`, `__flush_work`, `__cancel_work_timer`, `cancel_work_sync`, `p9_fd_close`, `p9_client_create`, `v9fs_session_init`, and VFS mount setup.

Control flow: several syz-executor tasks block in the same 9p close stack while creating v9fs sessions. The log then prints lock inventory, NMI CPU backtraces, an idle CPU stack, and a hung-task panic. The parser must collapse the repeated evidence into one report titled by `p9_fd_close`.

State and persistence behavior: static testdata persists repeated blocked tasks and a panic tail. It has no mutable state, but the repeated stacks encode a regression case for report deduplication and title stability.

Dependencies and integration points: depends on hung-task detection, workqueue-helper frame filtering, panic detection, and compatibility with many executor task names. It integrates 9p/V9FS mount initialization into report tests.

Risks: repeated nearly identical stacks can cause parser end-position or title instability. Generic cancellation frames should not hide the 9p-specific blocking function.

Test signals: multiple `INFO: task syz-executor... blocked`, `p9_fd_close+0x376/0x5c0`, `p9_client_create+0xa41/0x159b`, `v9fs_session_init`, and final `hung_task: blocked tasks` panic.
