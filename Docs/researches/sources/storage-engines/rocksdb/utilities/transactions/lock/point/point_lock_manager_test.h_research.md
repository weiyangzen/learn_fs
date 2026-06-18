# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_test.h

- **Purpose:** Shared GTest fixture and synchronization helper for point lock manager tests.
- **Important APIs/types/functions:** `PointLockManagerTest::init` creates a per-thread DB path, opens `TransactionDB`, configures four stripes and zero DB lock timeout, and records the wait sync point name. `SetUp` creates a separate `PointLockManager`; `TearDown` verifies no locks remain and destroys the DB. `NewTxn` starts a `PessimisticTransaction`. `UsePerKeyPointLockManager` swaps implementations. `BlockUntilWaitingTxn` starts a thread and waits until a sync point is reached.
- **Control flow:** Test cases inherit the fixture, add mock column families, create transactions with adjusted options, and use `BlockUntilWaitingTxn` to make a thread block inside lock acquisition before asserting intermediate state.
- **State and persistence behavior:** Fixture owns temp directory, `TransactionDB`, lock-manager shared pointer, environment pointer, and deadlock timeout override. Persistence is limited to temporary DB files destroyed at teardown.
- **Dependencies:** Depends on RocksDB file utilities, transaction DB APIs, test harness, point lock manager classes, common test helpers, and pessimistic transaction DB internals.
- **Integration points:** Used by `any_lock_manager_test.h`, `point_lock_manager_test.cc`, and stress tests.
- **Risks:** Tests create a lock manager separate from the DB's own manager, so fixture comments warn that this is intentional. `BlockUntilWaitingTxn` has a 30-second polling timeout to avoid hangs but may still be sensitive on very slow machines.
- **Test signals:** Provides standardized setup/teardown and lock-leak detection for all point-lock test files.
