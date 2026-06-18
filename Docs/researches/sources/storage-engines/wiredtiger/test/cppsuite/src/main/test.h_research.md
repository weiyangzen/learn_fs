# sources/storage-engines/wiredtiger/test/cppsuite/src/main/test.h

## Purpose
Declares the base `test` class and `test_args` struct used by cppsuite concrete tests.

## Important APIs, Types, And Functions
`test_args` carries `test_config`, `test_name`, optional `wt_open_config`, and `home`. `class test` inherits `database_operation`, deletes copy/assignment, exposes `init_operation_tracker` and virtual `run`, and stores protected `_args`, `_config`, `_timestamp_manager`, and `_operation_tracker`.

## Control Flow
The header defines ownership boundaries: framework components are private, while selected configuration and timestamp/tracker members are protected for test overrides. Concrete tests typically derive from `test`, call `init_operation_tracker` in the constructor, and override operation methods inherited from `database_operation`.

## State And Persistence Behavior
Private state includes enabled component pointers and an in-memory `database` model. Persistent WiredTiger state is managed indirectly through `run` and `connection_manager`.

## Dependencies And Integration Points
Includes `database_operation.h`, `metrics_monitor.h`, `workload_manager.h`, and `connection_manager.h`. This header is included by nearly every cppsuite test implementation.

## Risks And Test Signals
Because `_args` is stored by reference, the caller must keep the `test_args` object alive for the test lifetime. Custom tests can access protected internals, which is useful but can bypass lifecycle invariants.
