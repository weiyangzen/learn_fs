# sources/object-store/daos/src/vos/tests/vts_pm.c

## Purpose
`vts_pm.c` is the VOS punch-model and conditional-operation test suite. It validates array size and punch behavior through `vts_array`, object/dkey/akey/recx punch visibility, conditional update/fetch/punch semantics, minor-epoch punch ordering, aggregation after removals and uncommitted records, EC-size query behavior, and stress scenarios with many transactions and keys.

## Important APIs, Types, And Functions
`struct pm_info` stores the array object ID, array handle, epoch, and fixed update/fetch/fill buffers for array tests. `pm_setup` allocates and opens a VOS test array; `pm_teardown` closes and frees it. `struct counts` plus `count_cb`, `vos_check`, `vos_check_obj`, `vos_check_dkey`, `vos_check_akey`, and `vos_check_recx` provide recursive iterator assertions for visible and punched entries.

Array helpers include `array_set_get_size`, `array_size_write`, `array_read_write_punch_size`, and typed wrappers `array_1` through `array_4`. Punch-model helpers include `punch_model_test`, `simple_multi_update`, `object_punch_and_fetch`, `sgl_test`, `remove_test`, `small_sgl`, `minor_epoch_punch_sv`, `minor_epoch_punch_array`, and `minor_epoch_punch_rebuild`.

Conditional helpers are `obj_punch_op`, `cond_dkey_punch_op`, `cond_akey_punch_op`, `cond_fetch_op_`, `cond_updaten_op_`, and `cond_update_op_`. Stress and transaction helpers include `multiple_oid_cond_test`, `many_keys`, `test_inprogress_parent_punch`, `struct vos_ioreq`, `do_punch`, `do_io`, `many_tx`, `execute_op`, `uncommitted_parent`, `test_uncommitted_key`, and `test_multiple_key_conditionals_common`.

## Control Flow
`run_pm_tests` runs two CMocka groups: broad punch-model tests and PMDK/conditional tests. The array tests repeatedly reset array layout parameters, write data, read it back, shrink logical size with punches, and verify holes are filled with the sentinel fill buffer. `punch_model_test` layers updates and akey/dkey/object punches at successive epochs, checks fetch visibility before and after punches, validates recursive iterator counts with and without `VOS_IT_PUNCHED`, and verifies `vos_obj_query_key` max recx and max-write results.

The conditional suite first exercises single dkey/akey predicates, object punches, conditional fetches both with and without DTX, duplicate akey rejection, and many deterministic OIDs. Multi-key conditional tests use `DAOS_COND_PER_AKEY` to combine per-IOD akey predicates with dkey predicates, with and without explicit DTX commit. `many_tx` generates deterministic pseudo-random operations across object/dkey/akey grids, keeps a ring of in-flight transactions, periodically commits older DTXs, aggregates older epoch ranges, deletes objects, and repeats the run.

Minor-epoch tests create multi-op DTXs where update and punch share a major epoch but differ by operation sequence. They verify that a same-transaction punch hides the earlier minor update, array updates after punches remain visible where expected, and rebuild replay flags (`VOS_OF_REPLAY_PC`) order punch and update correctly.

## State And Persistence Behavior
The file is almost entirely about persistent state transitions. It checks that logical array size is represented through punches, punched entries may or may not be visible to iterators based on flags, holes preserve old fill values, object-level punches mask older children, and later updates after punches reestablish visibility. `remove_test` directly calls `vos_obj_array_remove` over epoch ranges and confirms aggregation preserves the same hole/data layout. Uncommitted-parent tests ensure later commits of parent punches or child updates resolve visibility correctly after DTX commit and aggregation.

EC-size simulation uses special recx indexes with `DAOS_EC_PARITY_BIT` and `VOS_GET_RECX_EC` to verify object size calculations across parity records, data holes, punched stripes, later parity, and merged holes. Conditional and many-transaction tests maintain prepared, committed, and skipped transaction states to exercise conflict and existence handling.

## Dependencies And Integration Points
The suite depends on `vts_io.h`, `vts_array.h`, VOS object/update/fetch/punch/query/aggregate APIs, DTX helper APIs, DAOS conditional flags, iterator APIs, and CMocka. It uses `setup_io`/`teardown_io` as the group fixture and per-test `test_args_reset` to isolate persistent pool state. `DAOS_ON_VALGRIND` reduces buffer/key counts for runtime control.

## Risks And Test Signals
This file contains expensive stress paths (`many_keys`, `many_tx`, `multiple_oid_cond_test`, EC simulation) and exact visibility expectations across complicated punch and DTX ordering. It is sensitive to changes in under-punch prevention, minor-epoch encoding, aggregation, object query-key semantics, and conditional flag interpretation. Strong signals include exact return-code assertions (`-DER_NONEXIST`, `-DER_EXIST`, `-DER_TX_RESTART`, `-DER_INPROGRESS`, `-DER_REC2BIG`, `-DER_NO_PERM`), buffer equality against expected holes/data, iterator counts for punched and visible entries, and EC object size values after each simulated stripe transition.
