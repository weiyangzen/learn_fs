# sources/storage-engines/rocksdb/util/heap_test.cc

Purpose: verifies `BinaryHeap` behaves like `std::priority_queue` over long pseudo-random operation streams while exercising RocksDB's replace-top optimization surface.

Important APIs/types/functions: defines `HeapTestValue`, parameter tuple `(MAX_HEAP_SIZE, MAX_VALUE, RNG_SEED)`, parameterized fixture `HeapTest`, and `TEST_P(HeapTest, Test)`. The test calls `BinaryHeap::push`, `replace_top`, `pop`, `top`, `empty`, and `clear`, comparing against `std::priority_queue`.

Control flow: each parameterized run chooses insert, replace-top, or pop by deterministic random distributions. Insertion is slightly more frequent until `MAX_HEAP_SIZE` is reached, then the test drains without inserting until empty. After every operation, it checks empty state and top value against the reference priority queue.

State and persistence behavior: all state is local to the test: random generator, `BinaryHeap`, reference heap, drain flag, and operation counters. It writes no persistent files and uses the `FLAGS_iters` gflag only to scale runtime.

Dependencies/integration points: depends on `util/heap.h`, GoogleTest, optional gflags, `port/stack_trace.h`, and standard random/queue utilities. It is the direct regression suite for the custom heap used by merge code elsewhere.

Risks: the test checks externally visible behavior, not exact comparison counts or root-cache behavior. It uses `assert` for some internal test invariants, so those checks depend on assertion configuration. Random streams are deterministic by seed but do not exhaustively cover every comparator or move-only type scenario.

Test signals: parameter sets cover a large heap with occasional duplicates, many duplicates, no-duplicate small heaps, two-element heaps, and one-element heaps. The test also verifies at least one max-size drain happens and that `clear` leaves the heap empty.
