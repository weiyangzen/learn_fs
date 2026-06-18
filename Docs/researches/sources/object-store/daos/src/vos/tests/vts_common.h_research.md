# sources/object-store/daos/src/vos/tests/vts_common.h

## Purpose

`vts_common.h` is the shared declarations and constants header for VOS tests. It defines common pool sizes, global fixture variables, test context structures, runner entry points, and DTX helper declarations.

## Important APIs, Types, And Functions

The header declares `struct vos_test_ctx`, `enum vts_ops_type`, pool-size macros (`VPOOL_256M`, `VPOOL_1G`, `VPOOL_2G`, `VPOOL_3G`, `VPOOL_SIZE`), and `FAULT_INJECTION_REQUIRED()`. It exposes fixture functions from `vts_common.c` and runner functions for pool, container, discard, aggregate, DTX, GC, persistent memory, I/O, timestamp, ilog, checksum, MVCC, WAL, evtree, tree, mark, and command tests.

It also declares `vts_dtx_begin()` and `vts_dtx_end()`, plus inline `vts_dtx_begin_ex()`, which begins a DTX and then overrides epoch bound and modification count before reinitializing reserved DTX state.

## Control Flow And Integration

Most test files include this header directly or indirectly through `vts_io.h`. Suite mains can call the `run_*_tests()` functions without knowing each file's static cmocka arrays. Test code uses `FAULT_INJECTION_REQUIRED()` to skip fault-injection-only cases when the build lacks support.

## State And Persistence Behavior

The header exposes globals such as `vos_path`, `gc`, `g_force_checksum`, `g_force_no_zero_copy`, `last_dkey`, and `last_akey`, making test behavior configurable across files. The DTX helper mutates a `struct dtx_handle` after attach, so it is tightly coupled to VOS internals.

## Risks And Test Signals

Because this header centralizes test runner declarations, signature drift will break build-time integration. The inline DTX helper relies on `vos_dtx_rsrvd_init()` succeeding after fields are modified; failures are caught by cmocka assertions in tests that use it.
