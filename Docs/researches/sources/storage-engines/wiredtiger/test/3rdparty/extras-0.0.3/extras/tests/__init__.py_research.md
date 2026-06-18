<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/__init__.py

Purpose: Test-suite aggregator for the vendored `extras` package.

Important APIs/functions: `test_suite()` imports `extras.tests.test_extras`, loads tests from that module through `unittest.TestLoader`, and returns a `unittest.TestSuite` containing those suites.

Control flow: The import happens inside `test_suite` to avoid loading tests at package import time. `map(loader.loadTestsFromModule, modules)` produces suites and wraps them in `TestSuite`.

State and persistence behavior: No durable state. It imports test modules and constructs in-memory unittest suites.

Dependencies and integration points: Depends on `unittest.TestSuite` and `TestLoader`. Used by Makefile and setup.cfg test configuration.

Risks: On Python 3, `map` is lazy but `TestSuite` accepts an iterable, so behavior is acceptable. Adding new test modules requires updating the hard-coded `modules` list.

Test signals: Invoked by `python -m testtools.run extras.tests.test_suite` and legacy setup test commands.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/__init__.py -->
