# sources/object-store/daos/src/vos/tests/vts_mvcc.c

## Purpose
`vts_mvcc.c` is a matrix-driven test suite for VOS multi-version concurrency control rules. It validates read/write conflict behavior, conditional operations, timestamp-only reads, listings, key queries, punches, distributed transactions, delayed commit/in-progress behavior, and epoch uncertainty checks against the MVCC rules documented in the VOS README.

## Important APIs, Types, And Functions
`struct tx_helper` tracks a current DTX handle, saved XID, operation counts, write counts, operation sequence, epoch uncertainty bound, and skip-commit state. `struct mvcc_arg` provides unique path/object generation, fail-fast behavior, base epoch, and delayed-commit control.

The operation model is `struct op`, combining operation name, type (`T_R`, `T_RTU`, `T_RW`, `T_W`), read/write hierarchy levels (`L_C`, `L_O`, `L_D`, `L_A`), read/write state predicates, and an `op_func_t`. The `operations` table lists fetches, conditional fetches, list operations, existence checks, max/min key queries, read timestamp updates, conditional updates, conditional punches, plain update, and plain punches.

Helper functions such as `set_path`, `set_oid`, `set_dkey`, `set_akey`, and `set_value` make deterministic overlapping hierarchy paths. `start_tx` and `stop_tx` lazily create DTX handles and commit, save, or clean them up. Wrappers `tx_fetch`, `tx_update`, `tx_punch`, `tx_list`, and `tx_query` adapt VOS APIs to the operation table.

## Control Flow
`conflicting_rw` iterates every read/read-timestamp/readwrite operation against every readwrite/write operation. `conflicting_rw_exec` generates overlapping paths and runs empty and nonempty cases across five epoch/transaction shapes: read epoch greater than write epoch, equal epochs in different TXs, equal epochs in the same TX, read epoch less than write epoch, and delayed commit for readwrite reads. `conflicting_rw_exec_one` prepares data when required, computes expected read and write results, handles known excluded DAOS-4698 cases when punch propagation is disabled, and verifies `-DER_TX_RESTART`, `-DER_EXIST`, `-DER_NONEXIST`, or `-DER_INPROGRESS` as appropriate.

`uncertainty_check` iterates every plain write against every non-read-timestamp operation. `uncertainty_check_exec` runs each pair with writes at the uncertainty bound committed, at the bound uncommitted, and above the bound. `uncertainty_check_exec_one` prepares nonempty state, executes the write under a DTX with a bound, then checks the later operation for restart, existence predicate failure, or success. Punches get special handling because parent punch prevention and read timestamp side effects can also produce `-DER_TX_RESTART`.

## State And Persistence Behavior
Each case uses a unique integer object/key path encoded from the matrix index and string path such as `coda`, so operations overlap at container, object, dkey, or akey levels while avoiding unintended cross-case collisions. The tests intentionally leave some DTXs uncommitted, save XIDs, later commit them, and rerun blocked operations to validate transition from in-progress to final conflict result. Read timestamp update operations use `VOS_OF_FETCH_SET_TS_ONLY`, and uncertainty checks use `th_epoch_bound` to validate timestamp uncertainty behavior.

## Dependencies And Integration Points
The file depends on `vts_io.h` for the VOS fixture and DTX helpers and `vts_array.h` through the test environment. It integrates through `run_mvcc_tests`, which reads `DAOS_DKEY_PUNCH_PROPAGATE` to decide whether DAOS-4698 excluded cases apply, and `CMOCKA_TEST_ABORT` for fail-fast behavior. It exercises `vos_obj_fetch_ex`, `vos_obj_update_ex`, `vos_obj_punch`, `vos_iterate`, `vos_obj_query_key`, `vos_dtx_commit`, and `vos_dtx_cleanup`.

## Risks And Test Signals
This suite produces a large matrix and is sensitive to exact MVCC semantics. Some TODOs in the file note that transaction begin/commit and epoch flow could be simplified, so the current harness is powerful but complex. Expected failures are exact error codes: `-DER_TX_RESTART` for stale/conflicting writes, `-DER_INPROGRESS` for delayed commit visibility, `-DER_EXIST`/`-DER_NONEXIST` for conditionals, and success when epochs or bounds permit the operation. The printed case identifiers are important diagnostics when a matrix entry fails.
