# sources/storage-engines/foundationdb/contrib/ctest_to_joshua.py

## Purpose
Packages CTest-discovered FoundationDB tests and required binaries into a Joshua-compatible tarball with a generated `joshua_test` runner script.

## Important APIs, Types, And Functions
`JoshuaBuilder` tracks source/build files to include. `add_arg()` rewrites command arguments and includes Python sibling dependencies and JAR classpaths. `_add_arg()` maps files under build dir to `build/...`, files under source dir to `src/...`, executables outside those roots to basename, and rejects unknown files. `_add_file()` strips debug symbols for `bin/` or `lib` archive paths. `get_ctest_json()` invokes `ctest -N --show-only=json-v1`.

## Control Flow
`main()` parses `--build-dir`, `--src-dir`, `--output`, and forwards unknown flags to CTest. It collects test commands, rewrites their args through `JoshuaBuilder`, adds standard FDB binaries and `libfdb_c`, emits a shell runner with library path setup, and writes a gzipped tarball.

## State And Persistence
Writes the output tarball. May create temporary stripped binaries during tar creation. Does not mutate the build or source tree.

## Dependencies And Integration
Requires CTest JSON output, `strip`, Python tarfile support, and FoundationDB build artifacts (`fdbbackup`, `fdbcli`, `fdbmonitor`, `fdbserver`, `mkcert`, `libfdb_c`). Integrates with Joshua test infrastructure.

## Risks
The `if "bin/" in arcfile or "lib" in arcfile` check can strip paths containing `lib` unexpectedly. Assertions handle unknown file locations and can be disabled with optimized Python. The generated script runs all commands with `set -euxo pipefail` and stops on first failure. Shared library selection only distinguishes Darwin vs non-Darwin.

## Test Signals
Use a synthetic CTest JSON with build files, source scripts, JAR classpaths, outside executables, and unknown files. Validate tar contents, executable mode of `joshua_test`, and stripping behavior.
