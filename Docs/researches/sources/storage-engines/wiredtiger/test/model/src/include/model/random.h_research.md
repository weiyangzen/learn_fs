# sources/storage-engines/wiredtiger/test/model/src/include/model/random.h

Purpose: provides a thin deterministic random wrapper around WiredTiger's `WT_RAND_STATE` plus probability/weight macros used by workload generation.

Important APIs and types: `random(uint64_t seed)`, static `next_seed`, `next_double`, `next_float`, `next_index`, `next_uint64()` overloads, and private `_random_state`. Macros `probability_switch`, `probability_case`, `probability_default`, `weight_init_block`, and `weight_init` implement compact weighted selection and total-weight initialization.

Control flow: generator code seeds `random`, asks for uniform floats/doubles or integers, and uses probability macros to choose operations. Weight macros build a closure that sums mutable weight fields in a spec object.

State and persistence: state is only the `WT_RAND_STATE`; no persistent data. Deterministic seeds create reproducible workloads and generated WT configs.

Dependencies and integration: includes `model/core.h` and WT internal header `wt_internal.h`, so it is tied to WiredTiger internals rather than standard C++ random. Used by `kv_workload_generator`.

Risks: `next_uint64(max)` multiplies a double by `max`, so distribution/bounds depend on floating-point behavior and assumes `max > 0`. `next_uint64(min,max)` assumes `max >= min`. Macros rely on hidden names and are sensitive to nesting.

Test signals: generator reproducibility tests should fix seeds. Unit checks should cover range bounds, `next_index(0)` handling if implementation rejects it, and probability branches with edge weights.
