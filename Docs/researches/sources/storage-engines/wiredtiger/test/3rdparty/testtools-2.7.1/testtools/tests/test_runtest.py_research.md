# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_runtest.py

## Purpose
This module tests `RunTest`, the object responsible for executing one `TestCase`, handling exceptions, and integrating custom test runners.

## Important APIs, types, and functions
`TestRunTest` validates `RunTest` construction, handler storage, result decoration, default result creation, `_run_core` invocation, keyboard interrupt propagation, on-exception callbacks, handled versus unhandled exceptions, last-resort logging, and guaranteed `stopTest`. `CustomRunTest` is a marker runner. `TestTestCaseSupportForRunTest` verifies constructor-supplied runners, class-level `run_tests_with`, method-level `run_test_with`, decorator arguments, decorator wrapping, and constructor precedence.

## Control flow
Tests define local `TestCase` subclasses and local `RunTest` subclasses, run them with `TestResult` or `ExtendedTestResult`, and inspect emitted events or return markers. Exception tests call private methods like `_run_user` and `_run_prepared_result` to validate precise behavior around propagation and result reporting.

## State and persistence behavior
State is local to runner instances: `case`, `handlers`, `last_resort`, `result`, and custom markers. No persistence occurs.

## Dependencies and integration points
It depends on public exports `ExtendedToOriginalDecorator`, `run_test_with`, `RunTest`, `TestCase`, and `TestResult`, plus matchers and `ExtendedTestResult`. It protects the execution path used by every testtools `TestCase.run()`.

## Risks and test signals
High-risk behavior includes not masking `KeyboardInterrupt`, still running teardown, invoking `addOnException` handlers, reporting unhandled `SystemExit` through last resort, and always calling `stopTest`. Custom runner precedence is also a user-visible contract.
