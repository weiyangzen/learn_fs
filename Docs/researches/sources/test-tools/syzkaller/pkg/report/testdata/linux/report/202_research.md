<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/202 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/202

## Purpose
This fixture validates suspicious RCU usage parsing for RDS TCP connection allocation. Expected title is `WARNING: suspicious RCU usage in rds_tcp_conn_alloc`, type `LOCKDEP`. It also includes a sleeping-function warning in invalid context.

## Important APIs, Types, And Functions
The report exercises lockdep/RCU warning parsing. Important frames include `__rds_conn_create`, `lockdep_rcu_suspicious`, `___might_sleep`, `__might_sleep`, `kmem_cache_alloc`, `init_timer_key`, `rds_tcp_conn_alloc`, `rds_tcp_conn_free`, `rds_cmsg_atomic`, `rds_conn_drop`, and syscall/context frames. The parser should recognize `WARNING: suspicious RCU usage` and the later `BUG: sleeping function called from invalid context at mm/slab.h:420`.

## Control Flow
The Linux reporter starts at the suspicious RCU usage warning, parses the held `rcu_read_lock` context, and uses the RDS TCP allocator as title context. Runtime flow is RDS connection creation calling an allocator that may sleep while inside an RCU read-side critical section.

## State And Persistence
The persistent fixture state is title, type, and 177 lines of raw log. Dynamic state includes lockdep context, task ids, RCU scheduler counters, and addresses.

## Dependencies And Integration Points
It depends on Linux RCU/lockdep suspicious usage regexes, invalid-context warning handling, and RDS stack frame title selection. It integrates as a parser case where `TYPE` is `LOCKDEP` rather than `WARNING`.

## Risks
The parser may select the generic `suspicious RCU usage` title without `rds_tcp_conn_alloc`, or switch to the later sleeping-function BUG as primary. It must also preserve the `LOCKDEP` type.

## Test Signals
Assert title `WARNING: suspicious RCU usage in rds_tcp_conn_alloc`, type `LOCKDEP`, and report text showing RCU read lock context plus RDS TCP allocation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/202 -->
