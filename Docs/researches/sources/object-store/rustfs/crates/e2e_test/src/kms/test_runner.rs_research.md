<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/test_runner.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/test_runner.rs

Purpose: this file defines a metadata-driven unified KMS test-suite runner with categories, criticality flags, estimated durations, result reporting, and two suite tests. It is intended to orchestrate KMS coverage but currently does not dispatch real tests.

Important APIs, types, and functions: `TestCategory` enumerates core, multipart, edge, fault, comprehensive, and performance categories. `TestDefinition` stores name, description, category, duration, and critical flag. `TestResult` records success/failure, duration, and error. `TestSuiteConfig` filters categories and critical-only mode. `KMSTestSuite` owns definitions and provides `filter_by_category()`, `filter_critical_tests()`, `get_category_summary()`, `run_test_suite()`, `run_single_test()`, and `print_test_summary()`. Tests are `test_kms_critical_suite()` and `test_kms_full_suite()`.

Control flow: `KMSTestSuite::new()` builds a static catalog of KMS test names matching other modules. `run_test_suite()` filters by config, logs a plan, loops through definitions, calls `run_single_test()`, records duration, sleeps two seconds between entries, and prints summaries. `run_single_test()` only logs a warning that dispatch is not implemented and returns success. The suite tests therefore validate the runner plumbing but not actual KMS functionality.

State and persistence: in-memory state is the test catalog, filter config, generated result list, durations, and summaries. No RustFS server or KMS state is created by the runner because dispatch is a placeholder.

Dependencies and integration points: depends on tracing, tokio sleep, `serial_test`, and KMS test naming conventions. Intended integration point is future dispatch to actual test functions or subprocess-driven cargo filters.

Risks: the biggest risk is false confidence: both suite tests pass even though every listed test is skipped by placeholder dispatch. `max_duration` and `parallel_execution` config fields are not enforced. Success-rate math divides by `results.len()`, which would be problematic if filters produce zero tests.

Test signals: current signals are limited to runner catalog/filter/summary behavior. They do not prove any KMS feature works until `run_single_test()` is implemented.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/test_runner.rs -->
