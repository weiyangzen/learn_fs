# sources/storage-engines/wiredtiger/test/cppsuite/src/main/database_operation.h

## Purpose
Declares the polymorphic workload surface used by cppsuite tests. The class provides default database population, workload operation, and validation hooks that tests can override selectively.

## Important APIs, Types, And Functions
`class database_operation` exposes virtual methods for `populate`, `background_compact_operation`, `checkpoint_operation`, `custom_operation`, `insert_operation`, `read_operation`, `remove_operation`, `update_operation`, and `validate`. The API receives framework primitives such as `database`, `thread_worker`, `timestamp_manager`, `configuration`, and `operation_tracker`.

## Control Flow
The header defines the framework contract rather than direct flow. `test` inherits from this class, `workload_manager` selects operation types, and `operation_configuration` binds `thread_type` values to these virtual member functions. Override granularity is per operation type, letting a test keep the standard run lifecycle while replacing only one workload lane.

## State And Persistence Behavior
No state is stored in this class. Persistence behavior is indirect: implementations create collections, mutate WiredTiger tables, record operation tracker rows, and validate disk state. Virtual dispatch means the actual persistence behavior can differ substantially by concrete test.

## Dependencies And Integration Points
Includes `database.h` and `thread_worker.h`. It is integrated by `test.h` as a base class and by `operation_configuration.cpp` via `std::bind` dispatch.

## Risks And Test Signals
The base contract assumes override methods obey `thread_worker` transaction semantics and stop promptly when `running()` becomes false. Tests that override tracking schema should also override `validate`, because the default validation expects standard tracking table formats.
