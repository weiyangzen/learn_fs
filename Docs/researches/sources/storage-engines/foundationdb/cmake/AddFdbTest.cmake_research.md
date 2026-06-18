# sources/storage-engines/foundationdb/cmake/AddFdbTest.cmake

## Purpose
Configures FoundationDB test registration, simulation test bookkeeping, correctness package staging, binding tester packaging, and client-test wrappers for CTest/Joshua workflows.

## Important APIs, Types, and Functions
Defines `configure_testing`, `verify_testing`, `add_fdb_test`, correctness package builders, `prepare_binding_test_files`, `package_bindingtester`, `package_bindingtester2`, `collect_unit_tests`, `add_python_venv_test`, `add_fdbclient_test`, `add_unavailable_fdbclient_test`, `add_multi_fdbclient_test`, and `add_java_test`.

## Control Flow and Integration
The module first records `.txt` and `.toml` simulation files, then each `add_fdb_test` removes assigned files from the unassigned list, filters by include/exclude settings, and emits a `TestRunner` CTest command. Packaging functions stage binaries, test files, CMake cache, Joshua scripts, local-cluster helpers, and generated language bindings into tarballs. Client tests run through a Python virtual environment and temporary cluster wrappers.

## State and Persistence
Depends on Python3, CTest, FoundationDB build targets (`fdbserver`, `fdbcli`, `fdb_c`, `fdb_flow_tester`), generated bindings, Java/Go/Swift options, `TestRunner`, Joshua scripts, and CMake package targets.

## Dependencies
Persistent build state is held in CMake parent-scope variables such as `fdb_test_files`, `TEST_NAMES`, `LONG_RUNNING_TEST_NAMES`, `TEST_FILES_<name>`, and custom targets/tarball outputs under the build tree. Runtime tests create logs, venv contents, cluster files, and package archives.

## Risks and Test Signals
Risks include stale unassigned-test detection, platform conditionals that skip Windows/IDE packaging, timeout differences under valgrind/sanitizers, shell quoting in venv commands, and binding package dependency ordering. Test signals are CTest registration output, `verify_testing` errors, generated tarballs, and successful temporary-cluster client tests.
