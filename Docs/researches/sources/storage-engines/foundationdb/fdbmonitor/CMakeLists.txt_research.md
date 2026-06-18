# sources/storage-engines/foundationdb/fdbmonitor/CMakeLists.txt

Purpose: build definition for the native `fdbmonitor` executable, its reusable static library, and its unit test executable.

Important targets: defines `fdbmonitor` from `fdbmonitor.cpp`, `fdbmonitor_lib` from `fdbmonitor_lib.cpp`, and `fdbmonitor_tests` from `fdbmonitor_tests.cpp`. Links `SimpleOpt`, `Threads::Threads`, and `rt` on non-Apple Unix. It imports include directories from `fdbclient`.

Control flow: the file creates targets, strips debug symbols for packaging, removes thread-sanitizer compile/link options from `fdbmonitor`, installs either the target or stripped binary depending on `GENERATE_DEBUG_PACKAGES`, and defines sandbox helper targets.

State and persistence behavior: creates `${CMAKE_BINARY_DIR}/sandbox/data`, `logs`, and a configured sandbox `foundationdb.conf` if absent. Adds `clean_sandbox`, `start_sandbox`, and `generate_profile` custom targets.

Dependencies and integration points: integrates with FoundationDB's CMake helpers (`strip_debug_symbols`, `fdb_install`), `Sandbox.conf.cmake`, `generate_profile.sh`, `fdbserver`, `fdbcli`, and optional `mako`.

Risks: comments identify an include-directory hack tied to the old build system. Disabling thread sanitizer is intentional because it changes observed restart behavior, but it also removes a class of instrumentation from this process.

Test signals: registers `add_test(NAME fdbmonitor_tests COMMAND fdbmonitor_tests)`, covering path and environment utility tests from the static library.
