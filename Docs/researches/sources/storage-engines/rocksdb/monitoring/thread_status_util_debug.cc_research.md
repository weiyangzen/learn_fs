# sources/storage-engines/rocksdb/monitoring/thread_status_util_debug.cc

Purpose: Implements debug-only helpers for thread-status tests and IO-activity expectations.

Important APIs/types/functions: `TEST_SetStateDelay` sets a per-state artificial delay. `TEST_StateDelay` sleeps when the configured delay is positive. `TEST_GetExpectedIOActivity` maps thread operation types to `Env::IOActivity` values.

Control flow: Delay functions use an atomic array indexed by `ThreadStatus::StateType`. Expected-activity mapping switches over known DB operations such as flush, compaction, DB open, get, multiget, iterator, checksum verification, entity gets, and manifest checksum retrieval; unknown operations map to `kUnknown`.

State and dependencies: Debug-only state is `static std::atomic<int> states_delay[NUM_STATE_TYPES]`. Depends on updater/util headers and `SystemClock`.

Risks/test signals: Only compiled under `!NDEBUG`. State index validity relies on valid `StateType` inputs. The operation-to-IO mapping is a test oracle for instrumentation paths and must be updated when new status operations imply new IO activities.
