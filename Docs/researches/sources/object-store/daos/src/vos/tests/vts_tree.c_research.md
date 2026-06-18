<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_tree.c -->
# sources/object-store/daos/src/vos/tests/vts_tree.c

## Purpose
`vts_tree.c` is a focused cmocka unit test for a VOS tree helper: `vos_irec_is_valid()`. It verifies the helper's NULL handling and DTX-local-ID matching behavior for internal record structures.

## Important APIs, Types, And Functions
The test uses `struct vos_irec_df`, specifically the `ir_dtx` field, and calls `vos_irec_is_valid(const struct vos_irec_df *, uint32_t)`. It defines `DTX_LID_VALID` and `DTX_LID_INVALID`, plus two static record fixtures: `valid` and `invalid_dtx_lid`.

`vos_irec_is_valid_test()` is the only test body. `tree_tests_all` registers it as `VOS1100: vos_irec_is_valid`, and `run_tree_tests()` invokes cmocka for the `tree` suite.

## Control Flow
The suite has no setup or teardown. It calls the helper three times: with a NULL record, with a non-NULL record whose `ir_dtx` differs from the caller's DTX local ID, and with a matching record. The expected results are false, false, and true.

## State And Persistence Behavior
There is no durable state, allocation, or tree mutation in this file. It is a pure unit check around interpretation of an in-memory VOS record descriptor. The persistence relevance is indirect: `vos_irec_is_valid()` is part of validating tree records that may be stored in persistent VOS layouts, so rejecting NULL or wrong-DTX records protects callers from treating unrelated on-media state as usable.

## Dependencies And Integration Points
The file includes cmocka headers and `vos_internal.h`, so it intentionally tests an internal helper rather than a public VOS API. `run_tree_tests()` is the external entry point used by the VOS test harness.

## Risks And Edge Cases
The coverage is intentionally narrow. It does not test boundary DTX IDs, special sentinel values, or records with other fields populated. Its value is as a regression tripwire for the exact validity predicate, especially NULL safety and equality against the supplied local DTX ID.

## Test Signals
A passing suite confirms that `vos_irec_is_valid(NULL, lid)` is false, a mismatched `ir_dtx` is false, and a matched `ir_dtx` is true. Any semantic change to the helper should be accompanied by updating this test because the expected truth table is explicit.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_tree.c -->
