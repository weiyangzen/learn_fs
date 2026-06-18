# sources/storage-engines/wiredtiger/test/cppsuite/tests/operations_test.cpp

## Purpose
Defines the baseline cppsuite operations test that uses all default `database_operation` behavior without overriding workload methods.

## Important APIs, Types, And Functions
`class operations_test : public test` has a constructor that calls `init_operation_tracker()`.

## Control Flow
All control flow is inherited from `test::run`, workload manager, and `database_operation`. Configuration determines which operation threads run, while default populate/insert/read/remove/update/checkpoint/custom/background compact/validation logic applies.

## State And Persistence Behavior
Uses the standard database model, operation tracker, timestamp manager, and validation behavior. Persistent effects depend entirely on the selected configuration file, such as insert-heavy or stress configurations.

## Dependencies And Integration Points
Includes `test.h` and uses the `test_harness` namespace. It is the simplest concrete class used by the test runner for standard stress workloads.

## Risks And Test Signals
Because no hooks are overridden, any special tracking schema or workload-specific validation is unavailable. It is useful as a broad signal for the base framework: successful population, configured operations, default validation, metrics output, and final success log.
