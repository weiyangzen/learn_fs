<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/206 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/206

## Purpose
This fixture validates corrupted suspicious-RCU parsing in a mixed memory-pressure and RDS report. Expected title is `WARNING: suspicious RCU usage`, type `WARNING`, and `CORRUPTED: Y`.

## Important APIs, Types, And Functions
The 323-line log contains `WARNING: suspicious RCU usage`, an enormous `vmalloc: allocation failure`, `Illegal context switch in RCU read-side critical section`, memory info, and later `BUG: sleeping function called from invalid context at mm/slab.h:420`. Important frames include `warn_alloc`, `__vmalloc_node_range`, `kvmalloc_node`, `xt_alloc_entry_offsets`, `translate_table`, `__rds_conn_create`, `lockdep_rcu_suspicious`, `___might_sleep`, `__might_sleep`, `rds_loop_conn_alloc`, and `rds_conn_create_outgoing`.

## Control Flow
The Linux reporter sees interleaved output from allocation failure and RCU/lockdep diagnostics. Because the expected report is marked corrupted and has a generic suspicious RCU title, the parser should not infer an allocator-specific RDS title as in reports 202 and 203. It must still classify it as a warning and flag corruption.

## State And Persistence
Persistent state is the expected metadata and long mixed console log. Dynamic state includes memory allocator counters, RCU state, task ids, lockdep state, and addresses.

## Dependencies And Integration Points
It depends on suspicious-RCU warning detection, corrupted-log heuristics, memory-info noise filtering, and warning type mapping. It integrates as a stress case for mixed concurrent console output.

## Risks
The parser may overfit to `rds_loop_conn_alloc` or netfilter allocation frames and emit a non-generic title. It may also misclassify as `LOCKDEP`, whereas the expected type is `WARNING`.

## Test Signals
Assert title `WARNING: suspicious RCU usage`, type `WARNING`, and `CORRUPTED: Y`. The selected report should include the illegal RCU context-switch line without relying on a stable allocator-specific title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/206 -->
