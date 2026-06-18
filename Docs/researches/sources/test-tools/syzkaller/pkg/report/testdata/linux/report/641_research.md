# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/641

## Purpose
This fixture covers a non-panicking scheduling-while-atomic report in `simple_recursive_removal` on arm64.

## Important APIs, types, and functions
Key frames include `__schedule_bug`, `__schedule`, `schedule`, `rwsem_down_write_slowpath`, `down_write`, `simple_recursive_removal`, `debugfs_remove`, `blk_release_queue`, `kobject_put`, `blk_put_queue`, `blkg_free`, `__blkg_release`, and `rcu_core`.

## Control flow
RCU softirq cleanup releases a block cgroup/queue, removes debugfs entries, attempts a sleeping rwsem write lock, and triggers scheduling-while-atomic.

## State and persistence behavior
The log persists preemption/atomic state, architecture call trace, and scheduler diagnostic lines.

## Dependencies and integration points
It tests atomic-sleep parsing for scheduling-while-atomic messages on arm64 block/debugfs cleanup paths.

## Risks and test signals
The parser must identify `simple_recursive_removal` as the actionable frame and classify `TYPE: ATOMIC_SLEEP`.
