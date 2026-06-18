# sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/my-gtest-main.cpp

Purpose: implements the common test executable entrypoint and records the executable path for tests.

Important APIs/functions: `get_executable()` returns a stored `boost::filesystem::path`; `main()` stores `argv[0]`, initializes Google Mock/Test, and returns `RUN_ALL_TESTS()`.

Control flow: executable path is stored in an anonymous-namespace `boost::optional`. `get_executable()` asserts it was initialized before use. Google Mock initialization covers Google Test initialization.

State/persistence: process-global optional path; no persistence.

Dependencies/integration: gmock/gtest, Boost optional/filesystem, and cpp-utils assert. Linked into test executables via `my-gtest-main`.

Risks: `argv[0]` may be relative depending on invocation. Global state is initialized once per process and not thread-protected, but test startup is single-threaded.

Test signals: every test executable linked against this library validates basic startup.
