# sources/storage-engines/tikv/components/tikv_util/src/topn.rs

Purpose: fixed-capacity collector for the largest `N` ordered values.

Important APIs/types/functions: `TopN<T>::new`, `push`, `pop`, `peek`, `len`, `is_empty`, and `IntoIterator`.

Control flow: values are wrapped in `Reverse<T>` inside a `BinaryHeap`, turning the heap top into the smallest retained value. Every push inserts first and pops once if length exceeds capacity.

State and persistence: in-memory heap only.

Dependencies/integration: general utility for bounded top-k calculations without sorting all inputs.

Risks: `pop` returns values from smallest retained to largest, not descending; `IntoIterator` is explicitly unordered; capacity zero accepts pushes then immediately discards them.

Test signals: tests cover zero capacity, one capacity, retained top values, pop order, and unordered iteration after sorting externally.
