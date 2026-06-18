<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/python_version_check.py -->
# sources/storage-engines/wiredtiger/test/evergreen/python_version_check.py

Purpose: verifies that the Python interpreter running a script matches the Python interpreter configured in CMake.

Important APIs: `get_python_version_string(python_path)` runs `<python> --version` and returns the stripped output.

Control flow: `main()` parses optional CMake cache path, search string, and verbose flag. It records `sys.executable` and version. If cache/search are provided, it scans the cache for the first matching line, reconstructs the path from the first slash onward, gets that interpreter's version, prints details in verbose mode, and exits success only when versions match.

State and persistence: reads `CMakeCache.txt`; writes only stdout/stderr.

Dependencies and integration: invoked by Evergreen after configure to ensure Python CMake selection matches task Python. Depends on CMake cache line format containing an absolute path with `/`.

Risks and test signals: if cache/search args are missing, `cmake_python_version` remains `None`, causing a mismatch and exit. Path extraction is Unix-centric. It compares full `Python X.Y.Z` strings, so patch-level differences fail even when ABI compatibility might be acceptable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/python_version_check.py -->
