# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/CMakeLists.txt

Purpose: Defines the `cpp-utils-test` build target and its helper executables. It is the central test manifest for cpp-utils coverage across crypto, pointers, process, tempfile, IO, data, logging, assertions, system, threading, value types, and `either`.

Important APIs and types: CMake constructs `cpp-utils-test_exit_status`, `cpp-utils-test_exit_signal`, and the main `${PROJECT_NAME}` executable. It links `my-gtest-main`, `googletest`, and `cpp-utils`, adds the test to CTest, enables style warnings, and activates C++14.

Control flow: CMake enumerates source files, builds small subprocess helper binaries first, then adds them as dependencies of the main test runner.

State and persistence behavior: Build-system state only; no runtime persistence. Helper binaries are runtime dependencies for subprocess/backtrace tests.

Dependencies and integration points: Integrates unit tests with CTest and production `cpp-utils` library.

Risks: Omitting a source here silently drops test coverage. Helper executable naming is coupled to tests that call subprocesses.

Test signals: Successful configure/build, all listed sources compiled, helper binaries available, and `add_test` running the suite.
