# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/431

Purpose: Linux reporter parse fixture for syzkaller. It expects `BUG: unable to handle kernel paging request in partition_sched_domains_locked`, alternate `bad-access in partition_sched_domains_locked`, type `MEMORY_SAFETY_BUG`, corrupted `N`, panicked `N`. The report covers a scheduler/cpuset domain rebuild fault.

Important APIs, types, and functions: this tests page-fault/oops parsing and bad-access alternate generation. Key frames include `rebuild_sched_domains_locked`, `update_flag`, `cpuset_css_offline`, `css_killed_work_fn`, `process_one_work`, and `worker_thread`.

Control flow: 39 log lines are parsed. The faulting context is cpuset offline work; the reporter must derive a memory-safety bug title from scheduler partitioning rather than worker helpers.

State and persistence behavior: expected fields persist in headers; parser state is transient.

Dependencies, integration points, risks, and test signals: this protects crash grouping for scheduler/cgroup teardown faults. Risks include selecting workqueue frames or missing bad-access alternate. Passing tests require memory-safety type, title/alternate equality, and non-panicked/non-corrupted flags.
