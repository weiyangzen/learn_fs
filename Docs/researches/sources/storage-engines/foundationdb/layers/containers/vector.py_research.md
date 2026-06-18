# sources/storage-engines/foundationdb/layers/containers/vector.py

Purpose: This file implements a sparse vector/array abstraction on FoundationDB. It stores only explicit values plus a sentinel value at the last index so vector size can be recovered without separate metadata.

Important APIs and types: `Subspace` provides tuple prefixing. `_ImplicitTransaction` supports `with vector.use_transaction(tr)` so array syntax can omit explicit transaction arguments. `Vector` exposes `size`, `push`, `back`, `front`, `pop`, `swap`, `get`, `get_range`, `set`, `empty`, `resize`, `clear`, `__getitem__`, and `__setitem__`.

Control flow: Public methods resolve either an explicit transaction or the thread-local implicit transaction, then call transactional private methods. `push` writes at current size, `pop` reads the last two explicit entries to preserve sparse default representation, `resize` clears or writes the last default sentinel, and `get_range` translates Python slice semantics into FDB range scans with synthesized default values.

State and persistence behavior: Values are tuple-packed under keys `(index)` within the vector subspace. Missing indices below the vector size read as `defaultValue`; the highest explicit key determines size. Thread-local implicit transaction state is process-local and restored on context exit.

Dependencies and integration points: It uses `fdb.api_version(22)`, tuple packing, `threading.local`, and FDB key selectors/range scans. The file includes destructive example/test functions.

Risks: Python iterator support is incomplete in the shown code because `_print_vector` iterates `for v in vector` without a visible `__iter__`. `_resize` calls `self.size()` from inside a transactional method without passing `tr`, relying on implicit state that may not exist. Tests should cover sparse expansion/shrink, negative and stepped ranges, swaps with default elements, pop edge cases, implicit transaction nesting, and Python 2/3 compatibility.
