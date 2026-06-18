# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/setup.py

## Purpose

This script defines setuptools packaging metadata for the Python implementation of the subunit test streaming protocol. In the WiredTiger source tree it packages the vendored `python-subunit` 1.4.4 test dependency, including its Python modules, runtime dependencies, test extras, and console conversion/filter tools.

## Important APIs, Functions, and Metadata

- `_get_version_from_file(filename, start_of_line, split_marker)` scans a file for lines starting with a marker, takes the last match, splits it on a marker, and returns the stripped right-hand value. It returns `None` for missing files or missing matches.
- `VERSION` is resolved from `PKG-INFO` `Version:` first, then from `Makefile` `VERSION=`, then falls back to `"0.0"`.
- `relpath = os.path.dirname(__file__)`; if non-empty, the script changes the working directory to the script directory so relative metadata files such as `README.rst` resolve correctly.
- `setup(...)` declares:
  - package name `python-subunit` and computed version;
  - README-based long description;
  - supported Python versions 3.7 through 3.12;
  - package list `subunit`, `subunit.tests`, and `subunit.filter_scripts`;
  - `package_dir={'subunit': 'python/subunit'}`;
  - `python_requires=">=3.7"`;
  - runtime dependencies `iso8601` and `testtools>=0.9.34`;
  - console scripts for v1/v2 conversion, filtering, listing, notification, output, stats, tags, CSV, disk export, GTK, JUnit XML, pyunit, and TAP conversion;
  - test/doc extras for `fixtures`, `testscenarios`, `hypothesis`, and `docutils`.

## Control Flow and State Behavior

At import/execution time the script computes `VERSION` by reading local metadata files. It changes process working directory to the setup script directory when invoked from another directory, then calls `setuptools.setup`. Packaging state is created by setuptools commands outside the script, such as build directories, egg-info, installed scripts, or metadata files. The script itself does not store runtime application state.

The version lookup intentionally prefers distribution metadata (`PKG-INFO`) over development checkout metadata (`Makefile`). The helper's list comprehension reads all matching lines and selects the last one, which allows later matching lines to override earlier ones but also means malformed duplicate metadata can affect the version.

## Dependencies and Integration Points

The script imports `os.path` and `setuptools.setup`. It reads `README.rst`, `PKG-INFO`, and `Makefile` relative to the package root. It exposes console entry points that target modules under `subunit.filter_scripts`, so packaging must include those modules and runtime imports must resolve the vendored `subunit` package. Runtime dependencies on `iso8601` and `testtools` match the modules used by `subunit.v2`, protocol tests, and result adapters.

## Risks and Maintenance Signals

- The helper uses `open(filename)` without an explicit encoding or context manager. That is acceptable for small local metadata files but can be brittle under unusual default encodings or static-analysis standards.
- If both `PKG-INFO` and `Makefile` are missing or malformed, the package version silently becomes `"0.0"`, which can confuse downstream packaging.
- The package list is explicit. Adding new import packages under `python/subunit` requires updating `setup.py` or they will not be installed.
- Console script entry points are a public CLI surface; renaming filter modules or `main` functions breaks installed tools.
- `tests_require` is legacy setuptools metadata; `extras_require['test']` is the more relevant modern dependency hook.

## Test Signals

Packaging signals are indirect: building the package, running `egg_info`, installing in a clean environment, invoking console scripts, and running the python-subunit test suite. The protocol and result test files in this work item also validate that declared runtime dependencies (`iso8601`, `testtools`) are sufficient for core behavior.
