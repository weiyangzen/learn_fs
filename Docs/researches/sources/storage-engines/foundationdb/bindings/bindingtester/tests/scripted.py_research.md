# sources/storage-engines/foundationdb/bindings/bindingtester/tests/scripted.py

## Purpose
`scripted.py` defines `ScriptedTest`, a fixed bindingtester scenario that exercises a broad cross-section of the stack-machine API: transaction lifecycle, reads/writes, range reads, key selectors, database-level operations, tuple packing/unpacking/ranges, atomic operations, versionstamps, unit tests, and optional thread instructions.

## Important APIs, Types, And Functions
- `ScriptedTest(Test)` uses `workspace` for data and `results_subspace` for expected result comparison.
- `setup(args)` forbids concurrency above 1 and bisection because the generated script is fixed and not designed for partial operation counts.
- `generate(args, thread_number)` creates a `ThreadedInstructionSet`, emits the long deterministic instruction script, and records expected results.
- `get_result_specifications()` compares result keys under `results_subspace`, filtering common retry/conflict errors.
- `get_expected_results()` returns the expected `Result` objects accumulated by `add_result()`.
- `append_range_test()` bulk-loads random key/value pairs and verifies range APIs across normal, starts-with, and selector variants.
- `add_result()` writes one result key with `SET_DATABASE`, appends the expected `Result`, then pops the live result value off the stack.

## Control Flow
The script begins with `ON_ERROR`, read-version, set/get/commit/reset scenarios; proceeds through snapshot and database reads, range clears, key selector queries, range-starts-with variants, tuple operations, integer arithmetic, tuple range boundaries, versionstamped key/value atomic operations, and `UNIT_TESTS`. If threads are enabled, it creates two thread specs, coordinates through wait keys, mutates a shared key, and accepts either thread's final value as expected.

## State And Persistence Behavior
The test persists workspace keys and result keys. Results are deterministic except for sections with accepted alternatives such as thread race outcomes. Versionstamp tests persist keys/values whose final location/content is only known after commit. Range tests clear and repopulate the workspace to avoid contamination from previous phases.

## Dependencies And Integration Points
It depends on `ThreadedInstructionSet`, `Result`, `ResultSpecification`, `test_util`, and the Python `fdb.tuple` implementation for expected packed values/ranges. It is one of the strongest compatibility contracts for bindingtester instruction semantics across languages.

## Risks And Edge Cases
Because the script is monolithic, small instruction semantic changes can affect many later expectations. It cannot be bisected by current harness assumptions. Versionstamp operations are API-version-sensitive (`SET_VERSIONSTAMPED_VALUE` with explicit index is gated at API >= 520). Threaded section intentionally has nondeterministic final value and must list both acceptable outputs.

## Test Signals
Expected results under `results_subspace` are precise behavioral assertions. The test covers error strings, empty results, range ordering/reversal, exact-mode invalid range limits, tuple encoding, versionstamp commit errors, and cross-thread database waits.
