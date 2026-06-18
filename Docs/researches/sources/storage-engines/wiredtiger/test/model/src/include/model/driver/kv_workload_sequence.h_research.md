# sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_sequence.h

Purpose: defines dependency-aware operation sequences used internally by the workload generator before flattening to a serial `kv_workload`.

Important APIs and types: `kv_workload_sequence_type` categorizes sequences (`checkpoint`, `checkpoint_crash`, `crash`, `evict`, `restart`, `rollback_to_stable`, timestamp setters, `transaction`, etc.). `kv_workload_sequence` stores a serial sequence number, type, deque of `operation::any`, dependency list, and unblock list. Methods include append operators, `size`, indexed access, `operations`, `overlaps_with`, `dependencies`, `unblocks`, and `must_finish_before`.

Control flow: the generator builds sequences, uses `overlaps_with`/`contains_key` to infer conflicts, calls `must_finish_before` to wire dependency edges, and later traverses runnable sequences through `kv_workload_generator::sequence_traversal`. `unblocks` lets completion of one sequence decrement dependency counts for followers.

State and persistence: this class has only transient scheduling state. It indirectly models persistence conflicts by identifying operations that touch overlapping table/key ranges and ensuring their relative order is preserved.

Dependencies and integration: includes `kv_workload.h`, `core.h`, and `data_value.h`. It is owned by `kv_workload_generator` and has no WT dependency.

Risks: dependency edges store raw pointers, so sequence objects must outlive traversal. `contains_key` must understand point and range operations correctly or the generator can produce invalid concurrent schedules. Sequence numbers are the equivalent serial schedule order and must remain stable for timestamp assignment.

Test signals: generator tests should create overlapping inserts/removes/truncates across tables and assert dependency detection. Non-overlapping sequences should remain independently runnable. `must_finish_before` should add reciprocal dependency/unblock relationships exactly once.
