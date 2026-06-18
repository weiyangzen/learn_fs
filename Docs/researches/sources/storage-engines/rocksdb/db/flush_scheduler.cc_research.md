# sources/storage-engines/rocksdb/db/flush_scheduler.cc

Implements `FlushScheduler`, a small lock-free stack of column families whose memtables may require flushing. It lets producers mark a CF for flush and consumers later take a Ref'ed CF to process.

`ScheduleWork(ColumnFamilyData*)` asserts no duplicate schedule in debug builds, refs the CF, allocates a `Node`, and pushes it onto `head_` with relaxed compare-exchange. `TakeNextColumnFamily()` pops the atomic head, deletes the node, removes it from the debug set, filters dropped column families, and returns a live Ref'ed CF. Dropped CFs are unrefed and skipped. `Empty()` checks whether `head_` is null and cross-checks debug state with allowance for races with scheduling. `Clear()` drains by repeatedly taking and unrefing CFs.

There is no persistent state. Runtime state is an atomic singly linked list plus debug-only duplicate tracking. Scheduling is LIFO rather than FIFO. Memory ownership is manual: each schedule adds a CF ref and node allocation, and draining/taking must release them.

Dependencies are intentionally narrow: `ColumnFamilyData` ref counting and dropped-state checks. The implementation relies on the header's external synchronization contract: most calls are under DB mutex or recovery single-threading, while concurrent `ScheduleWork()` and `Empty()` have limited guarantees.

Risks include duplicate schedules in release builds, manual ref/node ownership, relaxed atomic misuse if callers violate the synchronization model, and LIFO fairness. There is no dedicated test in this subset; behavior is indirectly exercised by DB flush scheduling and shutdown/recovery cleanup tests.
