# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/644

## Purpose
This fixture is another non-panicking scheduling-while-atomic report in `simple_recursive_removal`.

## Important APIs, types, and functions
The same block/debugfs/RCU stack family appears: `simple_recursive_removal`, `debugfs_remove`, `blk_release_queue`, `kobject_put`, `blk_put_queue`, `blkg_free`, `__blkg_release`, and `rcu_core`.

## Control flow
An atomic context cleanup path attempts recursive debugfs removal and blocks on a write semaphore, producing the scheduling-while-atomic diagnostic.

## State and persistence behavior
The persisted test data is the expected title/type plus raw stack evidence. There is no panic marker.

## Dependencies and integration points
It broadens coverage for repeated atomic-sleep reports around block queue release and simple filesystem removal helpers.

## Risks and test signals
The parser must treat it as `TYPE: ATOMIC_SLEEP` and avoid overfitting to architecture-specific details.
