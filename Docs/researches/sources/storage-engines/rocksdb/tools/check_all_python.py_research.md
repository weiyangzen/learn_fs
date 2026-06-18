<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/check_all_python.py -->
# sources/storage-engines/rocksdb/tools/check_all_python.py

## Purpose
This script performs a repository-local Python syntax check. It finds Python files under selected RocksDB directories and compiles each source file with Python's built-in compiler without writing bytecode.

## Important APIs, Types, and Functions
The script uses `glob.glob` to collect filenames and Python's `compile(source, filename, "exec")` to parse and syntax-check each file. It searches the hard-coded base directories `buckifier`, `build_tools`, `coverage`, and `tools`, with depth patterns `*`, `*/*`, and `*/*/*`.

## Control Flow
It initializes an empty `filenames` list, expands the base/depth/suffix patterns for `.py` files, then iterates through every path. For each file it reads the full contents, appends a trailing newline, and calls `compile`. If any file has invalid syntax or cannot be read, Python raises and the script exits nonzero. If all files compile, it prints `No syntax errors in N .py files`.

## State and Persistence Behavior
The script is read-only with respect to the repository. It keeps only an in-memory list of filenames and source strings. Because it uses `compile` directly rather than import machinery, it does not create `.pyc` files and does not execute module top-level code.

## Dependencies and Integration Points
The script depends only on Python 3 standard library functionality and current working directory layout. It is intended as a lightweight pre-commit or post-commit check for Python edits in the RocksDB repo. It intentionally avoids scanning all of `./` to reduce the chance of traversing linked external repositories.

## Risks and Edge Cases
The scan depth is capped at three path components under each base directory, so deeper Python files are skipped. The hard-coded base list misses Python files added elsewhere. Files are opened with default encoding, so non-default encoded sources could fail before compilation. Because files are not sorted or deduplicated, output count and processing order follow glob behavior and may vary by platform. The script catches syntax errors only; import errors, runtime failures, lint issues, and type errors are out of scope.

## Test Signals
The primary signal is the process exit code: zero means all discovered files parsed successfully, while any exception fails the run. The printed count is a useful sanity check that the glob patterns found the expected population.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/check_all_python.py -->
