# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/427

Purpose: Linux reporter parse fixture for syzkaller. It expects `KCSAN: data-race in find_next_bit / rcu_report_exp_cpu_mult`, type `KCSAN-DATARACE`, frame `find_next_bit`, corrupted `N`, panicked `N`. The report covers a race between RCU expedited CPU selection and reporting.

Important APIs, types, and functions: this tests KCSAN data-race parsing, dual-frame title generation, and `FRAME:` handling. Key frames include `find_next_bit`, `sync_rcu_exp_select_node_cpus`, `wait_rcu_exp_gp`, `rcu_report_exp_cpu_mult`, `rcu_report_exp_rdp`, and `rcu_exp_handler`.

Control flow: 32 log lines are parsed. The reporter must combine both racing functions into the title and preserve `find_next_bit` as the primary frame.

State and persistence behavior: the `FRAME:` header adds expected parser state beyond title/type. Runtime state is KCSAN report metadata and selected frame.

Dependencies, integration points, risks, and test signals: this protects KCSAN race grouping for RCU internals. Risks are dropping the second racing function or ignoring the frame header. Passing tests require KCSAN-DATARACE type, exact combined title, and frame equality.
