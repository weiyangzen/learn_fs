<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/gtest/CMakeLists.txt

Purpose: top-level GoogleTest build orchestration for Ganesha tests.

Important build surface: pulls in GoogleTest support, sets include paths and unit-test libraries/flags, and adds subdirectories for FSAL API and NFSv4 tests. It also builds standalone tests for examples and core structures such as red-black tree/hash distribution depending on local conditions.

Control flow/state: CMake creates test binaries but this file does not itself run Ganesha. The child `fsal_api` directory defines latency executables that embed/start Ganesha through the shared test harness.

Dependencies/integration: depends on GTest, pthread/C++ support, internal headers, `ganesha_nfsd`, libtirpc, optional LTTng, and gperftools depending on test family.

Risks: build-time availability of optional tracing/profiling libraries can gate tests. Several child tests are benchmarks more than deterministic unit tests and may be expensive to run manually.

Test signals: configure with unit tests enabled, build the gtest tree, and verify expected fsal_api and nfs4 binaries are produced.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/CMakeLists.txt -->
