# sources/sync-backup/borg/src/borg/testsuite/helpers/__init__test.py

Purpose: validates helper-level exit-code classification and aggregation.

Important APIs and control flow: parametrized `test_classify_ec` checks inclusive/exclusive ranges for success, warning, error, and signal classes across legacy and modern Borg exit-code bases. `test_ec_invalid` checks out-of-range and type errors. `test_max_ec` verifies severity ordering, with modern warning/error subcodes choosing the lower code within a class but more severe classes winning overall.

State and persistence: no persistent state.

Dependencies and integration points: depends on constants such as `EXIT_SUCCESS`, `EXIT_WARNING_BASE`, `EXIT_ERROR_BASE`, `EXIT_SIGNAL_BASE`, and helpers `classify_ec` and `max_ec`. It integrates with command exit handling and multi-error aggregation.

Risks: one assertion in `test_classify_ec` calls `classify_ec(ec) == ec_class` without `assert`, so this test currently only checks that valid ranges do not raise. `max_ec` carries most behavioral verification.

Test signals: invalid input exceptions and exact maximum-exit-code outcomes.
