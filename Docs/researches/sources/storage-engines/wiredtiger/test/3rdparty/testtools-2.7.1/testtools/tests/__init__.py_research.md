# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/__init__.py

## Purpose
This package initializer assembles the full testtools test suite. Its `test_suite()` function imports all major test modules and returns a scenario-expanded `unittest.TestSuite`.

## Important APIs, types, and functions
The single public API is `test_suite()`. It imports `matchers`, `twistedsupport`, `test_assert_that`, `test_compat`, `test_content`, `test_content_type`, `test_fixturesupport`, `test_helpers`, `test_monkey`, `test_run`, `test_runtest`, `test_tags`, `test_testcase`, `test_testresult`, `test_testsuite`, and `test_with_with`, then maps each module's own `test_suite()`.

## Control flow
Imports are intentionally inside `test_suite()` so package import remains light and optional dependencies can be skipped by individual modules. Module suites are collected, wrapped in a `TestSuite`, then passed to `testscenarios.generate_scenarios`, and wrapped again.

## State and persistence behavior
The module has no persistent state. Test collection is computed on demand.

## Dependencies and integration points
It depends on `unittest.TestSuite` and `testscenarios`. It is the discovery bridge for the vendored testtools tests and assumes each imported module exposes `test_suite()`.

## Risks and test signals
Failures here are usually discovery failures: missing optional modules, renamed test modules, or missing `test_suite()` functions. Its behavior is indirectly validated whenever the full vendored test suite is loaded.
