# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_version.py.cmake

- **Purpose:** CMake template for producing fdb_version.py from configured current/future/previous release version variables.
- **Source facts:** 4 lines, 192 bytes, executable=False.
- **Important APIs/types/functions:** CMake substitution variables: none.
- **Control flow:** No runtime control flow; CMake configures this template into a Python constants module before tests run.
- **State and persistence:** Persists configured version strings into the generated fdb_version.py module.
- **Dependencies:** Depends on CMake configure_file-style substitution and release-version variables from the FoundationDB build.
- **Integration points:** The generated Python file is imported by binary_download.py and upgrade_test.py to choose current, future, and previous release binaries.
- **Risks:** Incorrect configured versions can make upgrade tests download or select the wrong binaries.
- **Test signals:** Importability of the generated module and successful upgrade/binary-download tests are the relevant signals.
