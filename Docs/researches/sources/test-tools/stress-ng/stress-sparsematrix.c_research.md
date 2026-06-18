# sources/test-tools/stress-ng/stress-sparsematrix.c

## Purpose

`stress-sparsematrix.c` implements `sparsematrix`, a CPU/cache/memory/search stressor that compares multiple sparse-matrix storage methods under a deterministic insert, lookup, random lookup, and delete workload. Supported methods include chained hash, preallocated quick hash, dense mmap, optional Judy arrays, optional hash-of-Judy arrays, optional BSD circle queues, optional red-black trees, and optional splay trees.

## Important APIs, Types, and Functions

- `stress_sparsematrix_method_info_t` provides a common method interface: `create`, `destroy`, `put`, `del`, and `get`.
- `test_info_t` accumulates max object memory estimate, put/get durations and operation counts, and no-memory skip state per method.
- `value_map()` deterministically maps `(x, y)` to a nonzero expected value.
- Hash methods use `sparse_hash_table_t` / `sparse_hash_node_t`; quick hash uses `sparse_qhash_table_t` with preallocated nodes.
- Optional Judy methods use `Pvoid_t` arrays and Judy macros (`JLI`, `JLG`, `JLMU`, `JLFA`).
- Optional tree methods use BSD `RB_*` and `SPLAY_*` macros with global roots and object-memory counters.
- Optional list method uses BSD `CIRCLEQ` y-lists containing sorted x-lists.
- Dense mmap uses `sparse_mmap_t`, `stress_mmap_populate()`, `mincore`, and direct offset indexing.
- `stress_sparse_method_test()` is the shared workload runner and verifier for every method.
- `stress_sparsematrix()` parses options, clamps item counts to matrix capacity, runs one or all methods, records per-method metrics, and returns failure on verification mismatch.

## Control Flow

The stressor initializes per-method metric structures, reads the selected method, matrix size, and item count with maximize/minimize support, clamps item count to `size * size`, logs density from instance zero, and enters the synchronized run state. Each loop iteration runs either every method except the special `all` entry or the selected method.

For a method, `stress_sparse_method_test()` creates the backend, saves two random seeds, and uses those seeds to make the put and verification passes deterministic. The put pass generates random coordinates, computes `value_map()`, inserts only when `get()` returns zero, and records put operations and duration. The verification pass resets the seed and expects every coordinate to return the deterministic value. It then performs random gets and finally resets the seed again to delete inserted coordinates. Destroy returns an estimated object-memory footprint. On mismatch or put failure, the stressor reports failure.

After the loop, the stressor emits per-method get and put rates as harmonic mean metrics for methods that were not skipped for memory. It also logs geometric means in debug output.

## State and Persistence Behavior

All storage is transient heap, Judy, mmap, or global in-process tree/list roots. The dense mmap method maps anonymous private memory and uses `mincore()` during destroy to estimate resident pages. Red-black and splay methods use global roots and object-memory counters, making them non-reentrant but fine for one stressor process. No external files are written.

## Dependencies and Integration Points

The file integrates with stress-ng random number seeding, prime-number helper, memory-limit helper, mmap helper, metrics, option parsing, and continue flags. It conditionally depends on BSD queue/tree headers, libbsd red-black support, Judy headers/library, `mincore`, `math.h` `frexp()`/`pow()`, and platform word size for Judy support. The exported stressor is `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH`, `VERIFY_ALWAYS`, with max metrics sized to twice the number of methods.

## Risks and Edge Cases

Large sizes and item counts can request very large hash tables, Judy arrays, or dense mmaps. The dense mmap method checks free memory plus swap and size_t overflow, but memory pressure can still be high. Some delete methods zero values while tree methods remove nodes; the shared test only requires subsequent destruction and does not re-verify deletion semantics. The list insertion paths can leave a newly allocated y-node if x-node allocation fails, though destroy should clean reachable nodes if the handle survives. Global tree roots and static Judy pointer storage make these methods unsuitable for concurrent use inside one process without isolation.

## Test Signals

Strong signals include successful `--sparsematrix-method all` with verify, individual method runs, no-memory skips that do not fail the whole stressor, and metrics named "`<method> gets per sec`" and "`<method> puts per sec`". Build coverage should include configurations with and without Judy, libbsd RB trees, splay trees, and circle queues.
