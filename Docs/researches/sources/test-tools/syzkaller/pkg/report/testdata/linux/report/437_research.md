# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/437

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu` with expedited alternates, type `HANG`, corrupted `N`, panicked `Y`. The stack is nfnetlink network namespace exit waiting in `synchronize_net`.

Important APIs, types, and functions: frames include `synchronize_rcu_expedited`, `synchronize_net`, `nfnetlink_net_exit_batch`, `ops_exit_list.isra.0`, `cleanup_net`, workqueue helpers, and semaphore wait paths.

Control flow: 142 log lines are parsed. The parser must normalize the netfilter cleanup hang to the RCU synchronization title and preserve alternates.

State and persistence behavior: expectation headers persist parser fields; runtime state is temporary.

Dependencies, integration points, risks, and test signals: this protects RCU hang deduplication across network namespace cleanup subsystems. Risks include title drift to `nfnetlink_net_exit_batch`. Passing tests require HANG type, panic `Y`, exact alternates, and no corruption.
