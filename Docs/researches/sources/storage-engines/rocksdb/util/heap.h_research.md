# sources/storage-engines/rocksdb/util/heap.h

Purpose: implements `BinaryHeap`, a small max-heap optimized for RocksDB multi-way merge workloads where replacing the current top is common and consecutive winners often come from the same input stream.

Important APIs/types/functions: `BinaryHeap<T, Compare>` exposes `push`, `top`, `replace_top`, `pop`, `swap`, `clear`, `empty`, `size`, and `reset_root_cmp_cache`. Private helpers compute parent/child indexes and implement `upheap` and `downheap`. The container stores entries in `autovector<T>` and follows `std::priority_queue` ordering: `Compare` is a less-than relation and `top()` returns the maximum.

Control flow: `push` appends and bubbles a moved value up. `replace_top` overwrites the root and calls `downheap`, avoiding the pop-plus-push comparison cost. `pop` moves the last value to the root, removes the tail, then downheaps unless the heap is empty. `downheap` chooses the larger child and caches the root child comparison when only the root value changed, allowing repeated `replace_top` calls to skip one comparison pattern.

State and persistence behavior: all state is in memory: comparator, vector storage, and `root_cmp_cache_`. It does not persist data and does not own external resources. Cache validity is reset on `push`, `clear`, many downheap paths, and swap transfers it with the heap.

Dependencies/integration points: used by merge-like RocksDB internals that need faster replace-top behavior than `std::priority_queue`. It depends on `util/autovector.h`, standard comparison utilities, and `port/port.h` for assertions/platform setup.

Risks: methods assert on invalid use such as `top`, `pop`, or `replace_top` on an empty heap. Correctness relies on `Compare` remaining stable and compatible with the stored values. The root comparison cache is a performance optimization with subtle invalidation rules, so future mutation APIs must reset it carefully.

Test signals: `heap_test.cc` compares random operation sequences against `std::priority_queue`, including duplicates, small heaps, one-element/two-element heaps, growing and draining behavior, `replace_top`, `pop`, and `clear`.
