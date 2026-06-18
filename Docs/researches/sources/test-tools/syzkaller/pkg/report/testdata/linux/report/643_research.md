# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/643

## Purpose
This fixture is a panicking ARM scheduling-while-atomic report in `simple_recursive_removal`.

## Important APIs, types, and functions
Important symbols include `__do_softirq`, `panic`, `__schedule_bug`, `__schedule`, `schedule`, `rwsem_down_write_slowpath`, `down_write`, `simple_recursive_removal`, `debugfs_remove`, `blk_release_queue`, `kobject_put`, `blk_put_queue`, `__blkg_release`, and `rcu_core`.

## Control flow
Softirq/RCU cleanup releases block queue state and removes debugfs files, taking a sleeping rwsem while atomic. The kernel panics and also dumps another CPU stopping.

## State and persistence behavior
The file persists ARM backtrace format, panic state, and softirq preemption context.

## Dependencies and integration points
It verifies architecture-specific parsing for ARM backtraces and atomic-sleep panic reports.

## Risks and test signals
The parser must keep the same semantic title as report 641 while also preserving `PANICKED: Y`.
