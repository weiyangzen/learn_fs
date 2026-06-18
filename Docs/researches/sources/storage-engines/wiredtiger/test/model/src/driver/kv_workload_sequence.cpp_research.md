# sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_sequence.cpp

Purpose: implements sequence dependency helpers for generated workloads.

Important APIs and functions: `overlaps_with` checks whether this sequence's insert/remove/truncate operations touch keys or ranges touched by another sequence. `contains_key` checks exact key or range intersection for one table. `must_finish_before` adds a dependency edge from this sequence to another and a reverse unblocks edge.

Control flow and state: overlap detection iterates operation variants and only considers write-like operations that affect key ranges. Truncate range intersection checks endpoint containment and full containment. Dependencies are stored in vectors on the sequence objects.

Dependencies and integration: used by `kv_workload_generator` to preserve serial-equivalent semantics while later interleaving independent transactions. Depends on operation variants and `data_value` ordering.

Risks and test signals: the overlap model ignores read-only `get` and non-key special operations by design. Correctness depends on `data_value` comparisons matching table key ordering. Missed overlap dependencies can create unexpected WT conflicts; overly broad dependencies reduce concurrency coverage.
