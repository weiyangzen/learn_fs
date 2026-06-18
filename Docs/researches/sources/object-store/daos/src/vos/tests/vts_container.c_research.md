# sources/object-store/daos/src/vos/tests/vts_container.c

## Purpose

`vts_container.c` tests VOS container lifecycle APIs: create, open, query, close, destroy, UUID iteration, anchor reprobe, and handle reference counting.

## Important APIs, Types, And Functions

`struct vc_test_args` stores a pool file, pool UUID/handle, operation sequences for up to `VCT_CONTAINERS` containers, opened handles, container UUIDs, and an anchor flag. `co_ops_run()` executes per-container operation sequences using `vos_cont_create()`, `vos_cont_open()`, `vos_cont_query()`, `vos_cont_close()`, and `vos_cont_destroy()`.

Setup/teardown create and destroy one VOS pool via `vts_pool_fallocate()`, `vos_pool_create()`, `vos_pool_close()`, and `vos_pool_destroy()`. `co_uuid_iter_test()` directly prepares a `VOS_ITER_COUUID` iterator and validates every created container UUID is returned, optionally fetching an anchor and probing it back into the iterator.

## Control Flow

The suite has five cmocka cases. `VOS100` creates 100 containers and lets teardown destroy leftovers. `VOS101` runs create/open/query/close/destroy for all containers. `VOS102` and `VOS103` create containers, then iterate UUIDs without and with anchor reprobe. `VOS104` opens the same container 100 times, confirms destroy returns `-DER_BUSY`, closes all handles, and then destroys successfully.

## State And Persistence Behavior

All state is under a single temporary pool file. Container UUIDs are generated per test and cleared on destroy. Teardown defensively destroys any UUID still present and removes the pool file if it remains. Query tests assert newly created containers have zero objects and zero used bytes.

## Dependencies And Integration Points

The file uses `vts_common.h`, VOS internals, cmocka, UUID APIs, and VOS iterator APIs. It integrates with the broader runner through `run_co_test()`.

## Risks And Test Signals

Risks are reference leaks, iterator anchor invalidation, and cleanup failure after partial test execution. Passing signals include all lifecycle calls returning zero, query counters staying zero, iterator count matching `VCT_CONTAINERS`, and `-DER_BUSY` while open handles exist.
