# sources/storage-engines/wiredtiger/bench/workgen/workgen_func.c

## Purpose
`workgen_func.c` is a C bridge that lets C++ workgen code call selected WiredTiger internal helper functions without including broad internal headers directly in C++. It wraps atomics, clocks, epoch time, random state, zero-filled number formatting, and version string construction.

## Important APIs, Types, and Functions
The file defines the opaque `workgen_random_state` around `WT_RAND_STATE` and exports `workgen_atomic_add32`, `workgen_atomic_add64`, `workgen_atomic_sub32`, `workgen_clock`, `workgen_epoch`, `workgen_random`, `workgen_random_alloc`, `workgen_random_free`, `workgen_u64_to_string_zf`, and `workgen_version`. It also declares `WT_PROCESS __wt_process` so workgen links in cases where WiredTiger's common symbol is otherwise unresolved.

## Control Flow
Callers allocate RNG state with a `WT_SESSION`, use it repeatedly through `workgen_random`, then free it. Time and atomic wrappers delegate directly to `__wt_*` primitives. `workgen_version` writes `workgen-` plus `WIREDTIGER_VERSION_STRING` into a caller-provided buffer.

## State and Persistence Behavior
The only owned heap state is the RNG wrapper allocated by `malloc` and released by `free`. The random seed/state is initialized from a WiredTiger session implementation. No files are persisted.

## Dependencies and Integration Points
It depends on `wiredtiger.h`, `test_util.h`, and WiredTiger internal functions/macros such as `__wt_atomic_add_uint32`, `__wt_clock`, `__wt_epoch`, `__wt_random_init`, and `u64_to_string_zf`. `workgen.cpp` and `workgen_int.h` consume these wrappers through `workgen_func.h`.

## Risks and Edge Cases
The file casts public `WT_SESSION *` to `WT_SESSION_IMPL *`, so it is tightly coupled to WiredTiger internals. `workgen_version` uses `strncpy` in a way that may not null-terminate when the destination is very small. RNG allocation failure returns `ENOMEM`, so callers must not use an uninitialized state.

## Test Signals
Build/link tests are important because this bridge exists largely to satisfy linkage and C/C++ compatibility. Runtime smoke can allocate random state from a session, generate values, format a key string, and confirm version prefix output.
