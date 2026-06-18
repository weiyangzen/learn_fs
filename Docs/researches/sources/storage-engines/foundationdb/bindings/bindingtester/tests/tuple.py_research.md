# sources/storage-engines/foundationdb/bindings/bindingtester/tests/tuple.py

## Purpose
`tuple.py` defines `TupleTest`, a focused bindingtester workload for FoundationDB tuple integer encoding boundaries. It writes packed integer tuples for values around powers of two and compares resulting keys/values across bindings.

## Important APIs, Types, And Functions
- `TupleTest(Test)` owns a persistent `workspace` subspace for packed integer results and a `stack_subspace` for final stack logging.
- `setup(args)` records `max_int_bits` and `api_version`.
- `generate(args, thread_number)` iterates signs, bit positions, and offsets around powers of two, packs each value with `TUPLE_PACK`, stores it under a descriptive workspace key, commits periodically, logs the stack, and returns instructions.
- `get_result_specifications()` compares workspace contents and stack log, filtering common retry/conflict errors.

## Control Flow
Generation starts one transaction, computes min/max values from `max_int_bits`, and for every valid `sign * 2**i + offset` where offset is -10 through 10, it pushes a one-element tuple, packs it, pushes a label key, and stores. Every 5000 mutations it commits and resets to avoid oversized transactions. Finalization commits, logs stack, and commits again.

## State And Persistence Behavior
Persistent state is the workspace key/value set containing labels mapped to encoded tuple bytes, plus a stack log. The test intentionally uses deterministic labels so repeated runs with the same settings compare the same integer boundary cases.

## Dependencies And Integration Points
It depends on `fdb.tuple`, `InstructionSet`, `ResultSpecification`, and `test_util.blocking_commit()`. It integrates with bindingtester result comparison by exposing workspace and stack subspaces.

## Risks And Edge Cases
Coverage is intentionally integer-specific; other tuple types are tested elsewhere. Transaction size is controlled by periodic commits, but very high `max_int_bits` still expands operation count. Labels are strings packed into the workspace subspace, while values are binary tuple encodings, so both key and value encoding paths are exercised.

## Test Signals
Cross-binding equality of workspace contents is the direct signal for integer tuple packing compatibility near length/sign boundary transitions.
