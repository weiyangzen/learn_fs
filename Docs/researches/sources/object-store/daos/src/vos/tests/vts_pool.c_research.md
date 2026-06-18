<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_pool.c -->
# sources/object-store/daos/src/vos/tests/vts_pool.c

## Purpose
`vts_pool.c` is a cmocka test suite for the VOS pool lifecycle API. It validates pool creation against both pre-existing fallocated files and empty generated files, open/close/refcount behavior, destroy rules, pool query space accounting, exclusive-open locking, and data-format version compatibility. The tests exercise the same public VOS entry points used by higher VOS tests, but keep the scope at pool handles and pool metadata rather than object/container I/O.

## Important APIs, Types, And Functions
The central test fixture is `struct vp_test_args`, which owns generated pool filenames, operation sequences, create-mode flags, pool handles, and UUIDs. `pool_allocate_params()` allocates per-file operation arrays, handle slots, and UUID storage. `pool_set_param()` installs a sequence of `enum vts_ops_type` operations such as `CREAT`, `CREAT_OPEN`, `OPEN`, `CLOSE`, `DESTROY`, and `QUERY`.

`pool_ops_run()` is the generic executor. It dispatches operation sequences to `vos_pool_create_ex()`, `vos_pool_create()`, `vos_pool_open()`, `vos_pool_close()`, `vos_pool_destroy()`, and `vos_pool_query()`, then asserts expected zero returns and query invariants. The non-generic tests are `pool_ref_count_test()`, `pool_interop()`, `pool_open_excl_test()`, and `pool_interop_create_old()`.

## Control Flow
Each cmocka case starts with the common `setup()` allocation, a case-specific setup that builds the operation sequence, then either `pool_ops_run()` or a dedicated test body. `create_pools_test_construct()` creates one pool per CPU up to 16, so the create paths get light parallel-environment coverage without over-consuming bdev/aio file space. `pool_unit_teardown()` walks every configured pool, kills unfinished VOS pools via `vos_pool_kill()` if the sequence did not destroy them, removes files, and frees all arrays.

The lifecycle matrix covers create-only, create/open/close, create/destroy, create/open/query/close/destroy, create-open combined handle return, and fallocated versus generated-file backing. `pool_open_excl_test()` repeatedly recreates a pool to test all meaningful `VOS_POF_EXCL` conflicts: exclusive open with an existing opener, two exclusive openers, normal open with an exclusive opener, and create-open with exclusive flags.

## State And Persistence Behavior
The file is primarily concerned with durable pool metadata and handle state. It verifies that open handles hold a reference that makes `vos_pool_destroy()` return `-DER_BUSY` until all handles are closed. `pool_ops_run()` checks `vos_pool_query()` immediately after open: no containers, SCM total equal to `VPOOL_256M`, no NVMe space, free SCM below the raw total by at least `struct vos_pool_df`, and no NVMe free space.

WAL sizing is explicit for `vos_pool_create_ex()` through `VPOOL_TEST_WAL_SZ`, a 32 MiB WAL cluster-sized value. The tests do not replay WAL contents, but they ensure pool creation succeeds with WAL space in both fallocated and generated-file modes. `pool_interop()` and `pool_interop_create_old()` exercise persistent data-format version checks using fault injection and explicit version parameters.

## Dependencies And Integration Points
The suite depends on `vts_common.h` helpers for filename generation, fallocation, file existence checks, and `enum vts_ops_type`. It uses DAOS allocation/logging macros, UUID generation, cmocka assertions, and VOS internals from `vos_layout.h`, `daos_srv/vos.h`, and `vos_internal.h`. It also depends on fault-injection controls (`FAULT_INJECTION_REQUIRED()`, `daos_fail_loc_set()`) for interoperability cases.

`run_pool_test()` is the integration point registered with the broader VOS test runner. It formats a suite name with `dts_create_config()` and runs the `pool_tests` array under group setup/teardown.

## Risks And Edge Cases
Resource cleanup is important because unfinished pools can leave SMD_DEV/blob state; teardown calls `vos_pool_kill()` when the operation sequence did not finish with `DESTROY`. The operation executor assumes non-`QUERY` operations all succeed, so it is intentionally a positive-path matrix rather than a negative API validation suite. `create_pools_test_construct()` scales file count to CPU count, which improves coverage but can make failures dependent on local storage limits; the hard cap of 16 mitigates that.

The version tests require fault injection and may be skipped or invalid if fault injection is unavailable. The exclusive-open test reuses one UUID across repeated create/destroy cycles after regeneration once, relying on destroy to leave the pool path reusable.

## Test Signals
Primary pass signals are cmocka return codes from `run_pool_test()`. Useful behavioral assertions include `-DER_BUSY` for destroy with outstanding handles, `-DER_DF_INCOMPT` for injected incompatible pool format open, `-DER_INVAL` for too-old create version, successful open of `VOS_POOL_DF_2_4`, and `-DER_BUSY` for every exclusive-open conflict. Query assertions provide a regression signal for pool space accounting.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_pool.c -->
