# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/438

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu` with expedited alternates, type `HANG`, corrupted `N`, panicked `Y`. The report covers SIT tunnel network namespace cleanup blocked in RCU synchronization.

Important APIs, types, and functions: key frames include `synchronize_rcu_expedited`, `synchronize_net`, `rollback_registered_many`, `unregister_netdevice_many`, `sit_exit_batch_net`, `ops_exit_list.isra.0`, and `cleanup_net`.

Control flow: 155 log lines are parsed. Despite tunnel-specific teardown frames, the expected dedup key remains the synchronization function and its alternates.

State and persistence behavior: fixture text persists expected outputs; parser state is in-memory.

Dependencies, integration points, risks, and test signals: this pairs with report 432 for tunnel cleanup variants. Risks include splitting IPIP/SIT cleanup by caller. Passing tests require title/alternate normalization, HANG type, panic `Y`, and no corruption.
