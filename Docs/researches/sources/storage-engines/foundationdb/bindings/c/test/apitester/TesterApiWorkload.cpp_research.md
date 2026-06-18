# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterApiWorkload.cpp

## Purpose
`TesterApiWorkload.cpp` implements `ApiWorkload`, the reusable base class for C API tester workloads. It handles setup sequencing, random key/value generation, initial data population, workload progress control, tenant selection stubs, and common insert/clear/range-clear operations while maintaining an in-memory expected-value model.

## Important APIs, Types, And Functions
- Constructor reads workload options such as key/value lengths, max keys per transaction, initial size, existing-key read ratio, run-until-stop mode, operation counts, progress-check counts, key prefix, tenant count, and API version.
- `start()` schedules the workflow: clear data, create tenants if needed, workload-specific setup, populate initial data, then run tests.
- `getControlIfc()`, `stop()`, and `checkProgress()` support long-running workloads controlled by the manager.
- `runTests()` and `randomOperations()` execute either a fixed number of operations or until stopped.
- Random helpers generate keys, values, existing/non-existing keys, non-empty key ranges, tenants, and debug tenant strings.
- `populateDataTx()`, `populateTenantData()`, `clearData()`, and `clearTenantData()` seed and clear database state.
- `randomInsertOp()`, `randomClearOp()`, and `randomClearRangeOp()` are common transaction helpers used by derived workloads.

## Control Flow
All work is asynchronous through the workload scheduler and transaction executor. Methods call `execTransaction()` with a transaction body and success continuation. After commit succeeds, the local `stores[tenantId]` model is updated and the next continuation is scheduled. `randomOperations()` decrements counters atomically and loops through `randomOperation()`, which derived classes override.

## State And Persistence Behavior
Persistent state is restricted to keys under `keyPrefix` for this workload id, optionally per tenant. Local expected state lives in `stores`, an `unordered_map` from optional tenant id to `KeyValueStore`. Self-conflicting writes are used where needed so retries/timeouts do not leave older attempts in flight after a successful commit.

## Dependencies And Integration Points
It depends on `TesterApiWorkload.h`, `TesterUtil.h`, `test/fdb_api.hpp`, `fmt`, `WorkloadBase`, and `KeyValueStore`. Derived workloads in this subset rely on its helpers and local model.

## Risks And Edge Cases
Tenant support is partially stubbed: `createTenantsIfNecessary()` asserts false when tenants are configured, so tests with tenants cannot use this path yet. Random existing-key selection falls back to a generated key if the store is empty or selectors hit sentinels. Run-until-stop progress checks rely on atomics and scheduler ordering. Local model updates only occur after successful transaction callbacks.

## Test Signals
Derived workloads provide the direct behavior checks. `ApiWorkload` contributes setup/populate/clear correctness and progress confirmation for long-running tests.
