# sources/storage-engines/rocksdb/build_tools/build_detect_platform research

Purpose: `build_detect_platform` is the Makefile-facing platform detection script for RocksDB. It detects compilers, OS, CPU architecture, optional libraries, feature macros, Java/link settings, and writes a make-include file named by its first argument.

Important APIs: this is a shell script rather than a sourced function library. Its "API" is the generated variable file containing `CC`, `CXX`, `AR`, `PLATFORM`, `PLATFORM_*FLAGS`, Java flags, shared-library settings, version numbers, analyzer paths, feature flags, and dependency paths. It is configured through many environment variables, including `ROCKSDB_CXX_STANDARD`, `USE_CLANG`, `TARGET_OS`, `TARGET_ARCHITECTURE`, `PORTABLE`, `LIB_MODE`, `COMPILE_WITH_TSAN`, and `ROCKSDB_DISABLE_*`.

Control flow: the script validates the output path, initializes C++ standard and POSIX flags, optionally sources Meta fbcode config on internal hosts, chooses compiler tools, detects target OS, probes a faster linker on Linux, sets OS-specific flags, and then runs many compile/link probes unless cross-compiling or using fbcode. It detects fallocate, compression libraries, gflags namespace, NUMA, TBB, jemalloc/tcmalloc, memkind, adaptive mutexes, backtrace, profiling, sync_file_range, sched_getcpu, getauxval, aligned new, benchmark, folly, io_uring, warning support, CPU tuning, uint128, and dynamic loading. Finally it reads RocksDB version components and appends key-value lines to the output file.

State and persistence: it removes and recreates the output file, creates temporary compile artifacts such as `test.o` and `test_dl.o`, and derives state from the host compiler, libraries, filesystem, and environment. It cleans temporary test objects near the end.

Dependencies and integration: it relies on POSIX shell tools, `uname`, `hostname`, compilers, `build_tools/version.sh`, optional Homebrew, optional Meta `/mnt/gvfs` third-party trees, and the RocksDB Makefile consuming the generated variables.

Risks and test signals: feature detection is host-sensitive and can silently change build behavior. Compile probes may be skipped for cross/fbcode builds, so defaults must remain correct. There is a typo-like variable use `PLATFORM_CXXFALGS` in the `F_FULLFSYNC` probe, which can weaken that test. Tests should run the script under controlled env combinations, inspect generated variables, and verify representative Linux/macOS/internal-platform builds.
