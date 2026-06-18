# sources/storage-engines/foundationdb/contrib/monitoring/fdb_c_version.py

## Purpose
This script prints version information for an FDB C client library. It is a small diagnostic helper for confirming which `libfdb_c`/`fdb_c.dll`/`libfdb_c.dylib` is being loaded.

## Important APIs, Types, And Functions
`get_version_string(library_path)` loads the library with `ctypes`, selects API version 410, calls `fdb_get_client_version`, parses comma-separated version components, and returns a formatted client/source/protocol string. `error(message)` prints and exits. The CLI accepts an optional `library_path`.

## Control Flow
At startup, the script selects the default library name and loader terminology for Linux, Windows, or macOS, rejecting unsupported platforms. It parses the optional path, validates explicit files, defaults to the platform library name if omitted, and prints `get_version_string`.

## State And Persistence Behavior
The script is read-only. It loads a dynamic library into the process and calls C API functions but does not open a database or write files.

## Dependencies And Integration Points
It depends on Python `ctypes`, `argparse`, `platform`, `os`, and a compatible FDB C library. It integrates with monitoring or troubleshooting workflows where operators need to verify client binaries.

## Risks And Edge Cases
The selected API version 410 must be supported by the library. The version string parser assumes at least three comma-separated components. Loading by default name follows platform dynamic loader rules, which can find an unintended library from the environment. Error messages print byte strings directly for API selection failures.

## Test Signals
Tests should cover unsupported platform handling with mocks, explicit missing path rejection, load failure diagnostics, mocked C API version string parsing, and successful output formatting for representative client version strings.
