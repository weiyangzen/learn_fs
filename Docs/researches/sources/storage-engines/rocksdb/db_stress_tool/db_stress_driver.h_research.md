# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_driver.h

- **Purpose:** Declares the db_stress driver entry points used to run a `SharedState`/`StressTest` configuration.
- **Important APIs/types/functions:** Declares `ThreadBody(void*)` and `RunStressTest(SharedState*)` under `GFLAGS`.
- **Control flow:** Header only; implementation in `.cc` owns thread body and stress run orchestration.
- **State and persistence behavior:** No direct state; functions operate on `SharedState`.
- **Dependencies and integration points:** Includes `db_stress_shared_state.h` and `db_stress_test_base.h`; used by the db_stress top-level tool.
- **Risks:** The header has an include before `#ifdef GFLAGS`, so non-gflags consumers still parse `db_stress_shared_state.h`. API is intentionally narrow, so driver changes require updating only these declarations.
- **Test signals:** Compile/link coverage of db_stress driver and execution through `RunStressTest`.
