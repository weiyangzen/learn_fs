# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterAtomicOpsCorrectnessWorkload.cpp

## Purpose
`TesterAtomicOpsCorrectnessWorkload.cpp` defines `AtomicOpsCorrectnessWorkload`, a randomized API tester workload for FoundationDB atomic mutation semantics, including integer operations, byte min/max, append-if-fits, compare-and-clear, and versionstamped key/value operations.

## Important APIs, Types, And Functions
- `OpType` enumerates atomic operations from add/bitwise ops through compare-and-clear.
- `randomOperation()` chooses one operation type and dispatches to the appropriate test helper.
- `testIntAtomicOp()` encodes random integers to little-endian byte strings and compares output using an integer function.
- `testAtomicOp()` sets an initial value, conditionally applies an atomic op exactly once, reads the final value, and checks it against a local function.
- `testAtomicVersionstampedKeyOp()` validates `SET_VERSIONSTAMPED_KEY`.
- `testAtomicVersionstampedValueOp()` validates `SET_VERSIONSTAMPED_VALUE`.
- `testAtomicCompareAndClearOp()` verifies the key is removed when param equals current value.
- `WorkloadFactory<AtomicOpsCorrectnessWorkload>` registers `"AtomicOpsCorrectness"`.

## Control Flow
Every operation is a sequence of asynchronous transactions. The generic atomic path first writes `val1`, then starts a transaction that reads the key and only applies the atomic mutation if it still equals `val1`; this guards against applying non-idempotent atomic operations multiple times after `commit_unknown_result`. A final transaction reads and validates the result.

## State And Persistence Behavior
Each test uses random keys under the workload prefix. Persistent state is the atomic-operation target key and any resulting versionstamped key/value. The workload generally does not update `stores`; it validates directly against read-back values.

## Dependencies And Integration Points
It depends on `ApiWorkload`, `TesterUtil` integer conversion helpers, `fdb_c_options.g.h`, `fmt`, and the C++ C API wrapper in `test/fdb_api.hpp`.

## Risks And Edge Cases
Atomic operation idempotency under retry is explicitly handled for the generic path. Versionstamp tests depend on correct ten-byte placeholder plus four-byte offset encoding. `APPEND_IF_FITS` expectations assume generated values fit within FoundationDB value limits. Integer operations depend on little-endian conversion helpers.

## Test Signals
Failures are logged with expected/actual values and asserted. Coverage includes operations whose correctness is easy to regress in binding wrappers because they use raw mutation type enums and byte-level parameters.
