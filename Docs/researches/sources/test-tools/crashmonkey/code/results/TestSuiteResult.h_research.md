# sources/test-tools/crashmonkey/code/results/TestSuiteResult.h

Purpose: declares aggregate suite counters for CrashMonkey runs.

Important APIs/types: `ResultSet` stores pass/fixed/failed/fsck-required counts and data-failure subcounts. `TestSuiteResult` exposes tally methods, completed-count accessors, and result printing.

Control flow and integration: owned by `Tester` in a vector, with `current_test_suite_` pointing at the active instance.

State and persistence behavior: in-memory counters are persisted only through printed summaries.

Risks: `total_tests` is unused; the structure is not self-validating; no machine-readable export is provided.

Test signals: verify completed counts equal the sum of tallied categories and summary output remains stable for log consumers.
