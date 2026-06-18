# sources/object-store/daos/src/vos/tests/vts_gc.c

## Purpose

`vts_gc.c` stress-tests VOS garbage collection for deleted keys, objects, and containers. It builds large object/key/akey populations, deletes at different levels, manually tightens GC, and compares VOS-reported GC statistics with expected counts.

## Important APIs, Types, And Functions

`struct gc_test_args` owns a `credit_context` fixture and a boolean selecting single-value versus array-value updates. `gc_add_stat()` and `gc_print_stat()` maintain expected `struct vos_gc_stat` counters. `gc_obj_update()` writes either a single value through `vos_obj_update()` or an array value through zero-copy `vos_update_begin()`, `bio_iod_prep()`, `bio_iod_post()`, and `vos_update_end()`.

`gc_obj_prepare()` creates many objects, dkeys, akeys, and records. `gc_wait_check()` repeatedly calls `vos_gc_pool_tight()` until credits are available, then queries `vos_pool_query()` and compares `pif_gc_stat` to expected counters. `gc_key_run()`, `gc_obj_run()`, `gc_obj_run_destroy()`, and `gc_cont_run()` drive key, object, object-with-container-destroy, and container deletion scenarios.

## Control Flow

The cmocka cases cover key GC, object GC, object GC for array/bio records, container GC, destroying a container with outstanding objects, and object GC after closing/reopening a container. `gc_setup()` creates a 2 GiB SCM / 4 GiB NVMe-style fixture with 16 reusable credits; under Valgrind, object and dkey counts are reduced.

Each test resets fail locations, resets VOS GC counters with `VOS_PO_CTL_RESET_GC`, populates data, deletes the target level, enables GC fail-location forcing (`DAOS_VOS_GC_CONT` or `DAOS_VOS_GC_CONT_NULL`), and checks counters.

## State And Persistence Behavior

The tests create persistent pool/container state via `dts_ctx_init()`, update many VOS records, delete records or containers, and inspect GC statistics persisted in pool info. Array-mode updates intentionally write arbitrary data through bio paths because only allocation/freeing behavior matters.

## Dependencies And Integration Points

The file depends on `vts_io.h`, DAOS API headers, VOS pool/control/query APIs, object delete/key delete, container lifecycle, zero-copy bio internals, fail injection, and common credit helpers. It exports `run_gc_tests()`.

## Risks And Test Signals

Risks include counter drift, GC starvation, reopen-specific cleanup bugs, bio extent leaks, and mismatch between expected logical deletes and physical frees. Passing signals are exact `vos_gc_stat` matches, successful pool tightening, no leaked credit buffers, and successful cleanup in teardown.
