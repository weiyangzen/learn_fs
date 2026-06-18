# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/436

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in rtnl_lock`, alternate `hang in rtnl_lock`, type `HANG`, corrupted `N`, panicked `Y`. The log covers IPv6 address configuration work blocked acquiring RTNL.

Important APIs, types, and functions: key frames include `__mutex_lock`, `mutex_lock_nested`, `rtnl_lock`, `addrconf_verify_work`, `process_one_work`, and `worker_thread`.

Control flow: 132 log lines are parsed. Scheduler and mutex helpers must be skipped until the RTNL lock acquisition is selected; panic is set by the hung-task configuration.

State and persistence behavior: fixture headers persist expected title/type/panic. Runtime parser state is temporary.

Dependencies, integration points, risks, and test signals: this protects network configuration hang grouping. Risks include selecting `__mutex_lock` or workqueue frames. Passing tests require exact RTNL hang title/alternate, HANG type, panic `Y`, and non-corruption.
