<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/run.py -->
# sources/storage-engines/wiredtiger/test/suite/run.py

Purpose: Command-line runner for WiredTiger Python tests. It parses suite options, configures paths/build directory, loads hooks, discovers or selects tests/scenarios, applies batch/config/random filters, initializes `WiredTigerTestCase`, and executes via unittest or parallel concurrency.

Important APIs and types: Helpers include `usage`, `which`, `follow_symlinks`, `find`, `show_env`, `parse_int_list`, `verify_command_line_vars`, `restrictScenario`, `addScenarioTests`, `configRecord`, `configGet`, `configApplyInner`, `configApply`, `testsFromArg`, and `error`. Module globals include `wt_builddir` and `suitedir`.

Control flow: Startup sets Python paths through `test_util`, finds the build directory, and delays `wttest` import until ASAN env handling is complete. Main option parsing handles hooks, scenarios, batching, parallelism, dry-run, config files, seeds, ASAN restart, output handling, and command-line variables. It constructs a `WiredTigerHookManager`, calls `WiredTigerTestCase.globalSetup`, discovers tests or loads requested modules/groups, applies hook skip registration, random sampling, batch slicing, and finally calls `wttest.runsuite`.

State and persistence behavior: It may remove/recreate the suite test root via `globalSetup`, write config JSON files with `-C`, read skip lists/configs, set ASAN-related environment variables, and exec-restart Python for ASAN. It creates a random tiered object prefix for the run and passes seeds into suite random setup.

Dependencies and integration points: Integrates `test_util`, `testscenarios.generate_scenarios`, `discover`, `wthooks`, `wttest`, `unittest`, optional `concurrencytest` through `wttest.runsuite`, and extension/build-path discovery used by helpers.

Risks: Option parsing is manual and order-sensitive. ASAN restart depends on toolchain paths and environment. Scenario restrictions require a named test when `-s` is used. `testsFromArg` references `xrange`, which is only reached for numeric test ranges despite Python 3 enforcement.

Test signals: Exit status mirrors unittest success, dry-run prints selected tests, config-create output records suite hierarchy, batch/random filters select expected cases, and hook-driven skips/config changes appear in suite behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/run.py -->
