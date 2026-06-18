# sources/user-network-fs/samba/source3/torture/test_notify.c

Purpose: This file contains scalability and synchronization tests for SMB change notifications. It creates many outstanding notify requests, triggers directory changes, and uses barriers to coordinate concurrent notify registration and cleanup.

Important APIs/types/functions: `wait_for_one_notify_send()` opens a directory, issues `cli_notify_send()`, sends a `cli_chkpath_send()` barrier request to ensure the notify reached the server, and closes after notification. `run_notify_bench2()` starts many of these requests. `notify_bench3_send()` implements a longer state machine with `tevent_barrier` objects, directory creation, recursive notifications, subdirectory creation/deletion, delete-on-close, and close. Public entrypoints are `run_notify_bench2()` and `run_notify_bench3()`.

Control flow: Bench2 creates `\notify.dir`, opens `torture_nprocs` connections, starts `torture_numops` notify waiters per connection, waits until every waiter has passed the chkpath synchronization point, creates `\notify.dir\subdir`, then drains until all notifications close. Bench3 creates two barriers: a small barrier for per-round synchronization and a large barrier for notification/deletion phases. Each request opens a directory, waits with peers before registering notify, confirms registration, creates a related subdirectory, waits for notify delivery, deletes subdirectories, sets delete-on-close on the directory, and closes.

State/persistence behavior: Remote directory trees are created and removed under names such as `\notify.dir` and `\dirNNNNNNNN`. State includes many open directory handles, outstanding notify requests, tevent barriers, and counters. Persistence is intentionally temporary but cleanup is distributed across async callbacks.

Dependencies and integration points: The file depends on Samba SMB client async APIs, notification structures, tevent NTSTATUS helpers, security masks, `tevent_barrier`, and global torture concurrency knobs. It validates server notify scalability and ordering.

Risks: These are high-concurrency timing tests. Missed barrier participation, notification loss, or cleanup errors can hang or fail. Directory names in bench3 intentionally cross-reference neighboring indexes, so off-by-one changes can alter notification topology.

Test signals: Passing requires every notify to be registered before the trigger, all notifications to complete, all async state machines to return OK, and final `num_done` or `num_notifies` counters to reach expected values.
