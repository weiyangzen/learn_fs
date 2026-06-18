# sources/object-store/daos/src/vos/tests/vts_evtree.c

## Purpose

`vts_evtree.c` is a focused unit test for EVT descriptor validation. It checks that `evt_desc_is_valid()` rejects null descriptors, descriptors with invalid magic, and descriptors with an unexpected DTX local ID.

## Important APIs, Types, And Functions

The file constructs three static `struct evt_desc` instances: invalid magic, invalid DTX LID, and valid. `evt_desc_is_valid_test()` asserts the expected boolean result for each. `run_evtree_tests()` registers the single cmocka case.

## Control Flow, State, And Persistence

There is no VOS fixture, persistent pool, or tree allocation. The test is pure in-memory validation of descriptor fields against caller-supplied `DTX_LID_VALID`.

## Dependencies And Integration Points

It includes public EVT headers and `evt_priv.h`, plus cmocka. The suite name is fixed to `"evtree"` and does not use the `cfg` argument.

## Risks And Test Signals

The risk is narrow but important: accepting stale or corrupt evtree descriptors could allow invalid metadata traversal. Passing signal is exact rejection/acceptance for the four basic descriptor cases.
