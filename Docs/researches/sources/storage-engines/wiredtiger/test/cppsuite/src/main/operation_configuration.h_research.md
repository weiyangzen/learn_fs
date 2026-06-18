# sources/storage-engines/wiredtiger/test/cppsuite/src/main/operation_configuration.h

## Purpose
Declares a small helper that binds workload operation configuration to executable thread functions.

## Important APIs, Types, And Functions
`operation_configuration(configuration *config, thread_type type)` captures the parsed config pointer and operation type. `get_func(database_operation *dbo)` returns the operation callback. Public fields expose `config`, `type`, and `thread_count`.

## Control Flow
The header defines the dispatch object used by workload orchestration. It does not create threads itself; it supplies the thread function chosen in the `.cpp` implementation.

## State And Persistence Behavior
The class keeps a non-owning `configuration *` and immutable operation metadata. It does not persist data, but its selected callback determines database mutation behavior.

## Dependencies And Integration Points
Includes `<functional>`, `configuration.h`, `database_operation.h`, and `thread_worker.h`. It sits between workload configuration parsing and `thread_manager` thread creation.

## Risks And Test Signals
The public raw `configuration *` is non-owning and must remain valid while the operation configuration is used. `thread_count` is read at construction, so later config mutations would not be reflected.
