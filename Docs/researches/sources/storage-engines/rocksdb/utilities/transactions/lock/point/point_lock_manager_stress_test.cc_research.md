# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_stress_test.cc

- **Purpose:** Parameterized long-running correctness stress tests for both point lock manager implementations using randomized multi-threaded lock acquisition.
- **Important APIs/types/functions:** `PointLockCorrectnessCheckTestParam` configures manager type, thread/key counts, max keys per transaction, execution duration, lock type, lock timeout, lock expiration, allowed errors, and simulated work. `PointLockCorrectnessCheckTest` constructs the selected manager and invokes `PointLockValidationTestRunner`.
- **Control flow:** Each parameter opens the base `PointLockManagerTest` fixture, selects per-key or base manager, sets transaction options, then runs the validation runner for the configured duration and workload.
- **State and persistence behavior:** Exercises in-memory lock state heavily while the fixture owns a temporary TransactionDB. The runner maintains in-memory counters to validate exclusive/shared guarantees.
- **Dependencies:** Depends on the test fixture, validation runner, point lock managers, transaction DB options, and GTest parameterization.
- **Integration points:** Complements targeted unit tests with randomized stress coverage across myrocks-like timeout settings, short-expiration lock stealing, long-timeout deadlock detection, and low-contention workloads.
- **Risks:** Ten-second parameter cases can be expensive in CI. Some parameter sets allow non-deadlock errors to avoid false failures under short timeouts/expiration, so they are broader liveness/correctness signals rather than exact error-code assertions.
- **Test signals:** Validation runner asserts progress, no remaining locks, exclusive counter/value consistency, shared-lock read stability, and successful operation across both managers and lock type mixes.
