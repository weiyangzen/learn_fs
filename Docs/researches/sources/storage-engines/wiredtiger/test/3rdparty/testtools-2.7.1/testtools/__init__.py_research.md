# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/__init__.py

Purpose: public package facade for testtools extensions to Python unittest.

Important APIs, types, and functions: `__all__` re-exports core test case helpers, run machinery, test result adapters, stream result utilities, concurrent suites, fixture suites, skip decorators, version metadata, and `try_import`. It imports `Matcher` for documentation visibility, `RunTest`, `TestCase`, `PlaceHolder`, `ErrorHolder`, result classes from `testtools.testresult`, and suite helpers. Version detection uses `setuptools_scm.get_version()` when available, else falls back to `(2, 7, 1, 'final', 0)`.

Control flow: importing the package imports facade symbols from submodules, then tries dynamic version lookup relative to the package file. Lookup/import failures are swallowed for fallback versioning.

State and persistence: module global state is export bindings and `version`/`__version__`. No persistent storage is written.

Dependencies and integration points: integrates the package's internal modules into the stable public API and depends optionally on `setuptools_scm`.

Risks and test signals: fallback sets `__version__` but does not assign `version`, despite `version` being listed in `__all__`; code importing `testtools.version` may fail when `setuptools_scm` is unavailable. Test signals are public import coverage and version behavior in installed vs source-tree contexts.
