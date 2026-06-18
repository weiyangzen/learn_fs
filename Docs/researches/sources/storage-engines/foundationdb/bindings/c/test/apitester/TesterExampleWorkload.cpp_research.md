# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterExampleWorkload.cpp

## Purpose
`TesterExampleWorkload.cpp` defines `SetAndGetWorkload`, a minimal example API tester workload that writes one random key/value pair and reads it back.

## Important APIs, Types, And Functions
- `SetAndGetWorkload : public WorkloadBase` stores `keyPrefix` and a `Random`.
- `start()` calls `setAndGet(NO_OP_TASK)`.
- `setAndGet(cont)` writes a random key/value in one transaction, commits, then reads the key in a second transaction and logs an error if the value differs.
- Factory registration name is `"SetAndGet"`.

## Control Flow
The workload generates a key and value, calls `execTransaction()` to set and commit, then in the success continuation calls another `execTransaction()` to `get()` and compare the result before completing the provided continuation.

## State And Persistence Behavior
It persists one key/value under a workload-specific prefix. It does not clear prior data or maintain a local model beyond captured key/value variables.

## Dependencies And Integration Points
It depends on `TesterWorkload.h`, `TesterUtil.h`, `fmt`, the transaction executor inherited through `WorkloadBase`, and factory registration.

## Risks And Edge Cases
This is intentionally simple and not a stress workload. It logs mismatches but does not explicitly assert in the shown code path, so it is more demonstrative than comprehensive. Random keys can leave data behind unless surrounding harness cleanup handles it.

## Test Signals
The signal is a successful set/commit/get comparison through the C API tester framework, useful as a smoke test and example for new workloads.
