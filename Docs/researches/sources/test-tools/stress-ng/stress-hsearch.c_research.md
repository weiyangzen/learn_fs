# sources/test-tools/stress-ng/stress-hsearch.c

## Purpose
`stress-hsearch.c` exercises POSIX `hsearch()`-style hash table lookup or a local fallback implementation by inserting numeric string keys and repeatedly finding them.

## Important APIs, Types, And Functions
Options are `hsearch-size`, `hsearch-method`, and `hsearch-ops`. `stress_hsearch_method_t` maps method names to `hcreate`, `hsearch`, and `hdestroy` functions. The fallback uses `hash_table_t`, `hcreate_nonlibc()`, `hsearch_nonlibc()`, and `hdestroy_nonlibc()` with a prime-sized open-addressed table and a simple rotate/add hash. `stress_hsearch()` allocates keys, populates entries, scans finds, and optionally verifies returned data.

## Control Flow
The stressor selects libc or non-libc method, clamps size via stress-ng flags, creates a table with 25 percent slack, allocates key pointers, stringifies and inserts every index, waits at the sync barrier, then repeatedly finds all keys and verifies returned data when requested. Cleanup frees keys on Linux, frees the key array, destroys the hash table, and exits.

## State And Persistence
For fallback mode, `htable` and `htable_size` are static process-global state. Keys and table entries are heap allocations. There is no file or persistent state. Some platforms' `hdestroy()` ownership semantics differ, so cleanup intentionally avoids freeing keys except on Linux.

## Dependencies And Integration Points
It integrates with optional `<search.h>`, stress-ng prime checking, string duplication, memory diagnostics, process state, and verify/minimize/maximize flags.

## Risks
Libc `hsearch()` has process-global behavior on some systems, which can conflict if reused unexpectedly. Cleanup semantics differ across BSD/Linux. The fallback table uses index `0` as a sentinel and may degrade with clustering. Casting integer indices through `void *` assumes round-trip width is sufficient.

## Test Signals
Run libc and non-libc methods where exposed, verify finds for all inserted keys, exercise min/max table sizes, check low-memory behavior, and confirm platform-specific key cleanup does not double-free.
