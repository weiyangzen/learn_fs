# Research: sources/storage-engines/foundationdb/tests/TestRunner/pyproject.toml

- **Purpose:** Packaging metadata for the local fdb_test_runner Python package and its console-script entry points.
- **Source facts:** 12 lines, 280 bytes, executable=False.
- **Important APIs/types/functions:** Poetry package metadata with scripts {} and dependencies {}.
- **Control flow:** No runtime control flow; packaging tools read this metadata to expose console entry points.
- **State and persistence:** Persists package configuration only; it does not create runtime state.
- **Dependencies:** Declared dependencies include {}; Python version constraints and package name are controlled here.
- **Integration points:** Connects installed commands such as temporary-cluster, fake-cluster, multi-cluster, upgrade-test, and run-test-runner to Python module main functions.
- **Risks:** Script entry-point drift would break CI/test invocations even if module code still imports directly.
- **Test signals:** Package installation and console-script invocation are the primary validation signals.
