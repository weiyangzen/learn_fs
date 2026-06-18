# sources/storage-engines/rocksdb/util/defer_test.cc

Purpose: unit tests for `Defer` and `SaveAndRestore`.

Important tests: `DeferTest.BlockScope` verifies destructor execution at block exit. `DeferTest.FunctionScope` verifies deferred cleanup runs after lambda body changes state. `SaveAndRestoreTest.BlockScope` verifies original value restoration after mutation inside the guard scope.

Control flow: each test mutates an integer before and after entering a nested scope, relying on RAII destruction at scope exit.

State and persistence: local integer state only; no persistence.

Dependencies and integration: includes `util/defer.h`, port stack trace setup, and GoogleTest harness.

Risks: tests do not cover exception paths, moved/nontrivial types, null pointers, or destructor-throw behavior.

Test signals: confirms the primary RAII semantics used by production callers.
