# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/434

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu` with expedited alternates, type `HANG`, corrupted `N`, panicked `Y`. The stack is packet socket release and file close waiting in `synchronize_net`.

Important APIs, types, and functions: relevant frames include `synchronize_rcu_expedited`, `synchronize_net`, `packet_release`, `__sock_release`, `sock_close`, `__fput`, `task_work_run`, and signal/exit handling.

Control flow: 81 log lines are parsed. The hang is detected in a task-exit close path, but expected normalization remains the RCU synchronization function.

State and persistence behavior: static headers persist title/alternates; parser state is local.

Dependencies, integration points, risks, and test signals: this protects deduplication of packet release RCU hangs with other synchronization stalls. Risks include selecting `packet_release` or file close frames. Passing tests require HANG type, panic `Y`, alternates, and clean corruption state.
