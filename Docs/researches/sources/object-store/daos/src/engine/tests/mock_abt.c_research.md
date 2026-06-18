# sources/object-store/daos/src/engine/tests/mock_abt.c

Purpose: tiny Argobots mock object for tests that need `ABT_thread_yield()` at link time but do not need real Argobots scheduling.

Important APIs and functions: exports `int ABT_thread_yield(void)` returning `0`.

Control flow: no internal control flow beyond immediate success.

State and persistence: stateless and non-persistent.

Dependencies and integration: used by unit-test link targets where production code references Argobots yield but the test uses mocks/stubs. It avoids bringing in full ABT behavior.

Risks: tests linked against this mock cannot validate yield scheduling, fairness, or ABT error handling. It should only be used where yield side effects are irrelevant.

Test signals: successful link and tests that do not require real ABT progression.
