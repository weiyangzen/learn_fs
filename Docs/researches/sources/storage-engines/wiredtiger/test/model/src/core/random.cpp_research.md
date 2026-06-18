# sources/storage-engines/wiredtiger/test/model/src/core/random.cpp

Purpose: thin C++ wrapper around WiredTiger's internal pseudo-random generator for deterministic model workload generation.

Important APIs and functions: constructor seeds `WT_RAND_STATE` with `__wt_random_init_seed`. `next_double` and `next_float` scale `__wt_random` output to `[0, 1]` using `uint32_t` max. `next_index` returns a modulo index for a collection length. `next_uint64` combines two 32-bit random values into one 64-bit value.

Control flow and state: all state is the embedded `WT_RAND_STATE`; methods advance it in place. The header also supplies range helpers, probability macros, and weight initialization macros used by the workload generator.

Dependencies and integration: includes `model/random.h`, which imports `wt_internal.h`. Used heavily by `kv_workload_generator` for reproducible table, key, operation, timestamp, and stress-configuration choices.

Risks and test signals: `next_index(0)` would divide by zero; callers must ensure nonempty collections. Modulo and floating scaling are sufficient for tests but not uniform for all ranges. Deterministic seeds are the key test signal for reproducing generated workloads.
