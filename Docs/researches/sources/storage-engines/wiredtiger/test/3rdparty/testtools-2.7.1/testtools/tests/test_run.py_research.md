# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_run.py

## Purpose
This module tests the `testtools.run` command-line runner and `TestToolsTestRunner` behavior.

## Important APIs, types, and functions
Optional fixtures create temporary importable packages: `SampleTestFixture` for a normal or broken package, `SampleResourcedFixture` for a `testresources`-optimized suite, and `SampleLoadTestsPackage` for `load_tests` discovery. `TestRun` tests listing, loader-aware custom listing, failed import output, `--load-list` filtering and ordering, custom suite preservation, failfast, traceback locals, stdout routing, and discovery package `load_tests`.

## Control flow
Tests use temporary packages appended to `testtools.__path__` or `sys.path`, call `run.main()` or instantiate `run.TestProgram`, and inspect captured `StringIO` or fixture streams. Some tests expect `SystemExit` from the runner and assert exit codes. `--load-list` tests create a file containing requested test ids and verify only matching tests run or list.

## State and persistence behavior
Temporary packages and list files are created through fixtures and cleaned up. The module mutates `testtools.__path__`, `sys.modules`, `sys.path`, `sys.stdout`, and `unittest.defaultTestLoader._top_level_dir` in scoped ways.

## Dependencies and integration points
It depends on `doctest`, `io`, `sys`, `unittest`, `testtools.run`, optional `fixtures` and `testresources`, and matchers. It is the direct test surface for the CLI runner used by downstream consumers.

## Risks and test signals
Runner tests are sensitive to Python discovery behavior, syntax-error formatting, optional dependency availability, stdout handling, and `SystemExit`. The resource-suite test protects against flattening optimized suites when filtering.
