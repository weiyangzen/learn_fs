# sources/storage-engines/wiredtiger/test/3rdparty/testscenarios-0.4/lib/testscenarios/tests/__init__.py

Purpose: test-suite loader for the `testscenarios` package tests and README doctest.

Important APIs, types, and functions: `test_suite()` creates a standard suite and delegates to `load_tests()`. `load_tests()` builds test module names for `test_testcase` and `test_scenarios`, loads them with a `unittest.TestLoader`, adds a `doctest.DocFileSuite("../../../README")`, sets doctest report flags, and wraps the result with `testscenarios.generate_scenarios`.

Control flow: runner calls `test_suite()` or the `load_tests` protocol; tests are loaded by name, README doctests are appended, and scenario-bearing tests are expanded before returning the loader's suite class.

State and persistence: no persistent state. It modifies doctest's unittest report flags process-wide through `doctest.set_unittest_reportflags`.

Dependencies and integration points: depends on `doctest`, `sys`, `unittest`, and `testscenarios`. Integrates with `Makefile check` via `testscenarios.test_suite`.

Risks and test signals: the README doctest path is relative and can break if package layout or working-directory assumptions change. Test signal is the package suite loading both unit modules plus README doctests under `testtools.run`.
