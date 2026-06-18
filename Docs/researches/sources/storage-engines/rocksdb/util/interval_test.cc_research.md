# sources/storage-engines/rocksdb/util/interval_test.cc

Purpose: tests `IntervalSet` behavior for integer intervals and comparator-based `Slice` intervals, including merge, containment, open-ended intervals, and propagation mode return semantics.

Important APIs/types/functions: uses `IntervalSet<int>`, `Interval<int>`, `IntervalSet<Slice, Comparator>`, `BytewiseComparator`, `insert(start, end)`, `insert(start)`, iterators, `size`, `start`, `end`, and `has_end`.

Control flow: `BasicTest` inserts overlapping and adjacent integer intervals and checks canonical merged ranges. `SliceTest` inserts bounded and open-ended key ranges under the bytewise comparator and verifies contained inserts do not create new ranges. `PropModeTest` constructs the set with propagation mode enabled and verifies `insert` returns `false` when the inserted interval is already covered.

State and persistence behavior: interval state is purely in-memory and local to each test. No DB state is opened despite using `db_test_util` for the harness and stack trace setup.

Dependencies/integration points: validates `rocksdb/data_structure.h` interval utilities with both native ordering and RocksDB comparator ordering. Slice tests model key-range tracking behavior used by higher-level DB components that reason about key intervals.

Risks: coverage is focused on simple merge and containment cases. It does not stress randomized intervals, custom comparators beyond bytewise, reverse iteration, deletion, or very large interval sets. The final `SliceTest` leaves a trailing comment marker but no functional gap.

Test signals: confirms overlapping intervals collapse, disjoint intervals remain ordered, point/open-ended intervals are represented correctly, and propagation mode distinguishes new coverage from already-covered inserts.
