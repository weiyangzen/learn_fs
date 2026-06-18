# sources/object-store/rustfs/crates/e2e_test/src/policy/test_runner.rs

Purpose: orchestration harness for running the policy variable tests as a suite against an existing RustFS server. It provides categorization, result aggregation, optional critical-only filtering, pacing between tests, and summary logging.

Important APIs/types/functions: `TestCategory` enumerates SingleValue, MultiValue, Concatenation, Nested, and DenyScenarios. `TestDefinition` describes test name, category, and criticality. `TestResult` records success or error. `TestSuiteConfig` carries `include_critical_only`. `PolicyTestSuite::new`, `with_config`, `run_test_suite`, `run_single_test`, and `print_summary` implement the suite runner. Ignored `test_policy_critical_suite` invokes the runner with critical-only filtering and fails if any result failed.

Control flow: `run_test_suite` initializes logging, creates `PolicyTestEnvironment` for `127.0.0.1:9000`, waits for TCP readiness, filters definitions, runs each named test by dispatching to the corresponding `_impl_with_env` function in `policy_variables_test.rs`, sleeps two seconds between tests, and logs pass/fail summary.

State and persistence behavior: shares one external-server environment across all policy variable cases, so users/policies/buckets are created and cleaned by each test. Results are in-memory only. The runner does not checkpoint progress or isolate server state beyond serial execution and per-test cleanup.

Dependencies and integration points: depends on `PolicyTestEnvironment`, policy variable implementation functions, `serial_test`, Tokio sleep, `Instant`, and tracing. It integrates multiple ignored test functions into one ignored aggregate test.

Risks: matching by test-name string is fragile; adding a test to `PolicyTestSuite::new` requires updating `run_single_test`. `print_summary` divides by `results.len()` and would be invalid for an empty suite. The environment readiness check is only TCP-level. The runner assumes fixed port 9000 and external server lifecycle.

Test signals: useful aggregate signal for the policy variable critical path, especially for CI jobs that intentionally start RustFS out of band and run ignored E2E suites.
