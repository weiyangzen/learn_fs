# sources/object-store/daos/src/vos/tests/vts_common.c

## Purpose

`vts_common.c` provides shared fixture and resource helpers for VOS tests. It creates temporary pool files, initializes standalone VOS state, creates/destroys pools and containers, and manages reusable I/O credit buffers.

## Important APIs, Types, And Functions

The file exports `vts_file_exists()`, `vts_alloc_gen_fname()`, `vts_pool_fallocate()`, `vts_ctx_init()`, `vts_ctx_fini()`, `dts_ctx_init()`, `dts_ctx_fini()`, `dts_credit_take()`, and `dts_credit_return()`. Global `vos_path` and `gc` select file names; `oid_cnt` is reset during context initialization.

`vts_ctx_init()` is a compact pool/container fixture based on `struct vos_test_ctx`. It creates a pool file name, removes stale files, generates pool/container UUIDs, calls `vos_pool_create()`, `vos_cont_create()`, and `vos_cont_open()`, recording setup progress in `tc_step`. `vts_ctx_fini()` unwinds based on `tc_step`.

`dts_ctx_init()` is the broader I/O fixture for `struct credit_context`: initialize DAOS debug, call `vos_self_init()`, open/create pool, open/create container, then allocate credit buffers. `dts_ctx_fini()` reverses those steps. `vts_credits_init()` allocates each credit's value buffer; `dts_credit_take()` and `dts_credit_return()` manage the available-credit slots.

## Control Flow

The fixture code uses explicit state machines (`TCX_*` and `DTS_INIT_*`) so partial initialization can be unwound safely. Pool initialization fallocates an SCM file, then chooses create or open based on `tsc_create_pool()`. Container initialization similarly creates conditionally and always opens. Finalization falls through from the highest initialized step to clean lower layers.

## State And Persistence Behavior

Pool state is file-backed under `vos_path`, with generated `vpool.N` names. `vts_pool_fallocate()` creates a 256 MiB file, while `pool_init()` allocates `tsc_scm_size`. Destroy paths call VOS pool/container close and destroy operations; test files are freed/destroyed by callers. Credit state is in memory and must have no in-use credits at finalization.

## Dependencies And Integration Points

The file depends on Linux file APIs, fallocate, DAOS/VOS public and internal headers, DAOS debug initialization, cmocka assertions, and `vts_common.h`. It is the foundation used by container, GC, I/O, DTX, ilog, and aggregation tests.

## Risks And Test Signals

Risks include leaked file descriptors, incomplete cleanup after setup failure, stale files, and mismatched credit accounting. The test signal is mostly fixture reliability: suites can create/destroy isolated pools repeatedly without leftover containers, memory buffers, or pool files.
