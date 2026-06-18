# sources/storage-engines/wiredtiger/test/cppsuite/CMakeLists.txt

Purpose: Defines the cppsuite test harness static library and executable test targets.

Important APIs/types/functions: `add_library(cppsuite_test_harness STATIC ...)` compiles harness sources from bound, common, component, main, storage, and util directories. `create_test_executable` produces `run`, `test_live_restore`, `csuite_style_example_test`, and `test_disagg_failover_perf`. `add_test` registers ctest entries and labels smoke-test targets.

Control flow: the harness library is built first, gets the cppsuite include directory, compiler diagnostics, `test_util`, and `-DEXTSUBPATH=""`; executables link it. Antithesis builds additionally link `wt::voidstar`.

State and persistence: creates build artifacts and ctest metadata only.

Dependencies/integration: integrates cppsuite into the top-level CMake test framework and relies on `create_test_executable` from the parent build system.

Risks and test signals: every listed source must remain in sync with the harness source tree. `ctest -L cppsuite` or `ctest -R cppsuite` is the build/test signal.
