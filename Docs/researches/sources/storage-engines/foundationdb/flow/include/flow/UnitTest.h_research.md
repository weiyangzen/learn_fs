# sources/storage-engines/foundationdb/flow/include/flow/UnitTest.h

## Purpose
Flow's lightweight unit-test registration framework for ordinary and actor-based `Future<Void>` tests with optional parameters and data directories.

## Important APIs, Types, And Functions
`UnitTestParameters` stores named string parameters, typed getters, and a data directory. `UnitTest` records test name/file/line/function and links into `g_unittests`. `UnitTestCollection` stores the linked-list head. `TEST_CASE` registers static tests unless `FLOW_DISABLE_UNIT_TESTS` is set. `ACTOR_TEST_CASE` is actor-compiler generated. `noUnseed` disables RNG-state checking.

## Control Flow
Static `UnitTest` objects register at program startup. Runners iterate `g_unittests` and invoke registered functions. Actor source is rewritten so actor test bodies return `Future<Void>`.

## State And Persistence Behavior
Registration is process-global and non-durable. Test data directories may point tests at persistent scratch space, but this header only carries the path.

## Dependencies And Integration Points
Depends on `flow/flow.h`. Used by `UnitTestRunner`, `UnitTestWorkload`, and test cases across Flow, fdbrpc, fdbclient, and fdbserver.

## Risks And Edge Cases
Tests in unlinked translation units are not discovered. Unit tests can mutate global runtime state and may pass standalone while breaking simulation. Disabling tests suppresses registration but leaves disabled function declarations.

## Test Signals
Signals include path discovery, parameter parsing, actor test registration, data-dir setup, disabled-test behavior, and simulation RNG-state checks.
