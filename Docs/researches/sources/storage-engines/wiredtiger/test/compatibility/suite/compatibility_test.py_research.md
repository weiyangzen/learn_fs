# sources/storage-engines/wiredtiger/test/compatibility/suite/compatibility_test.py

Purpose: Python unittest harness for running compatibility test methods under different WiredTiger branch builds and Python bindings.

Important APIs/types/functions: `CompatibilityTestCase` extends the WiredTiger abstract test case. `run_method_on_branch` generates a temporary Python script that rewires `sys.path`, imports branch-specific `wiredtiger`, recreates class and instance state via pickle, calls `finishSetupIO`, and invokes a selected method in a subprocess. `assert_captured_output_contains` checks captured stdout/stderr files. `make_branch_scenarios`, `add_branch_pair_scenarios`, `global_setup`, `prepare_tests`, `run_tests`, and `run` prepare branches, build scenarios, and execute suites.

Control flow: global setup initializes test dirs, IO, random state, and current WiredTiger path. Preparation discovers required build configs, builds every suite branch/config combination, validates test-declared older/newer branch constraints, and combines branch-pair scenarios with any test-local scenarios. Each compatibility test then executes branch-specific phases in child interpreters.

State and persistence: creates per-test directories, temporary scripts under the test dir, branch build trees, captured output files, and serialized test attributes. Temporary scripts are removed only after successful subprocess execution.

Dependencies/integration: uses `compatibility_common`, `WTVersion`, `abstract_test_case`, `testtools`, `test_result`, `test_util`, `wtscenario`, branch-specific Python bindings, and Python `unittest`.

Risks and test signals: pickling test state can miss non-picklable or intentionally skipped attributes; subprocess failures leave scripts for diagnosis. Scenario validation catches unsupported branches early. Success is standard unittest success after all generated branch pairs pass.
