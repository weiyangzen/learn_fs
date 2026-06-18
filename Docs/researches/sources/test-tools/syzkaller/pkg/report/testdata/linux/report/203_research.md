<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/203 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/203

## Purpose
This fixture is the RDS loopback counterpart to report 202. Expected title is `WARNING: suspicious RCU usage in rds_loop_conn_alloc`, type `LOCKDEP`, with a sleeping-function invalid-context line later in the report.

## Important APIs, Types, And Functions
The static log exercises suspicious RCU usage matching and title extraction. Important frames include `__rds_conn_create`, `lockdep_rcu_suspicious`, `___might_sleep`, `__might_sleep`, `kmem_cache_alloc_trace`, `rds_loop_conn_alloc`, `rds_loop_conn_free`, `__init_waitqueue_head`, `rcutorture_record_progress`, `__lockdep_init_map`, `rds_conn_drop`, and `__raw_spin_lock_init`.

## Control Flow
The parser should detect the RCU warning, parse the held `rcu_read_lock` context, and select `rds_loop_conn_alloc` as the allocator that sleeps in the invalid context. Runtime flow is RDS loop connection creation inside RCU read-side protection.

## State And Persistence
Persistent state is the expected metadata and 177-line log. Dynamic values include lockdep state, CPU/task identifiers, and memory addresses.

## Dependencies And Integration Points
It integrates with Linux RCU/lockdep warning parsing, RDS stack title heuristics, and report test comparison. It complements report 202 by ensuring TCP and loopback allocators remain distinguishable.

## Risks
Parser title selection could collapse to `__rds_conn_create` or the later `BUG: sleeping function called from invalid context`, losing the allocator-specific title. Type could also regress from `LOCKDEP` to `WARNING`.

## Test Signals
Expected title `WARNING: suspicious RCU usage in rds_loop_conn_alloc` and type `LOCKDEP`. The report should include RCU read-lock context and the `rds_loop_conn_alloc` stack.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/203 -->
