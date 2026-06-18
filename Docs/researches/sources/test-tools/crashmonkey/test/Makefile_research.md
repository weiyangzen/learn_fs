# sources/test-tools/crashmonkey/test/Makefile

Purpose: self-contained Google Test/Google Mock makefile for building CrashMonkey unit tests. It compiles gtest/gmock libraries and selected project test binaries.

Important APIs/types/functions: variables `GTEST_DIR`, `GMOCK_DIR`, `CPPFLAGS`, `CXXFLAGS`, `TESTS`, `CODE_DIR`, targets for `gtest.a`, `gmock.a`, `RandomPermuterTest`, `PermuterTest`, `DiskWriteTest`, `DiskModTest`, `CmFsOpsTest`, `WorkloadTest`, and `TesterTest`.

Control flow: `all` builds `$(TESTS)`, currently `DiskModTest CmFsOpsTest WorkloadTest`; additional test targets are defined but not in the default list. Each object target compiles a test source with gtest headers, and each binary links project implementation files plus gtest/gmock libraries.

State/persistence behavior: creates object files, static gtest/gmock libraries, and test executables in the test directory; `clean` removes them. Dependencies/integration: relies on vendored googletest at `../googletest`, C++11, pthread, optional `SYS_HEADERS`, and Linux kernel headers for block flag tests.

Risks/test signals: default `TESTS` omits several defined tests, dependency rules are conservative, and some targets may need `-ldl` or kernel headers depending on environment.
