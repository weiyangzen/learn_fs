# sources/storage-engines/foundationdb/fdbclient/fdbclient_test.cpp

Purpose: executable entry point for fdbclient unit tests under simulation.

Important APIs and control flow: `initializeSimulation` resets client knobs with randomization enabled for simulated mode, then starts the unit-test simulator. `main` calls `runUnitTests` with suite name `fdbclient` and the initializer.

State and persistence: test runtime state is simulated and knob-driven. No production persistence is performed directly by this file.

Dependencies and integration: includes `Knobs.h`, `fdbrpc/simulator.h`, and `flow/UnitTestRunner.h`. The unit tests registered across fdbclient translation units are linked into this runner.

Risks: all fdbclient unit tests depend on correct simulator startup. Randomized knobs can expose issues but may also require deterministic seed handling when diagnosing failures.

Test signals: running the `fdbclient` unit-test executable is the primary signal; this file is required for tests such as the `VersionVector.cpp` cases to execute.
