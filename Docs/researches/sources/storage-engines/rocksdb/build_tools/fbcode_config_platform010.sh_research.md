# sources/storage-engines/rocksdb/build_tools/fbcode_config_platform010.sh research

Purpose: `fbcode_config_platform010.sh` is the platform010 successor to `fbcode_config.sh`. It sets compilers, sysroot-like include restrictions, dependency paths, RocksDB feature macros, and linker flags for Meta internal platform010 builds.

Important APIs: when sourced, it exports `CC`, `CXX`, `AR`, `AS`, `CFLAGS`, `CXXFLAGS`, `EXEC_LDFLAGS`, `EXEC_LDFLAGS_SHARED`, `VALGRIND_VER`, `JEMALLOC_LIB`, `JEMALLOC_INCLUDE`, `CLANG_ANALYZER`, and `CLANG_SCAN_BUILD`. It consumes `PIC_BUILD`, `USE_CLANG`, `ROCKSDB_DISABLE_*`, `USE_SSE`, and `PORTABLE`.

Control flow: the script sources `dependencies_platform010.sh`, starts with an invalid sysroot to prevent accidental default-library use, selects `_pic` variants when `PIC_BUILD` is set, builds include/lib variables for compression, gflags, benchmark, jemalloc, numa, libunwind, TBB, liburing, and kernel headers, defaults SSE and portability, selects GCC or Clang compiler branches, appends POSIX and RocksDB feature macros including io_uring, constructs static dependency linker flags and platform linker flags, then exports the environment.

State and persistence: there are no file writes; the sourced shell environment is the state. The dependency versions are pinned indirectly through `dependencies_platform010.sh`.

Dependencies and integration: it assumes Meta GVFS third-party roots, binutils, GCC/Clang layouts, platform010 runtime paths, and RocksDB's Makefile/build scripts. `build_detect_platform` sources this file for internal platform010 host builds.

Risks and test signals: it is not portable outside Meta. The deliberate `/DOES/NOT/EXIST` sysroot improves hermeticity but makes missing includes fail hard. ABI correctness depends on consistent pinned paths. Tests should source under GCC/Clang and PIC/non-PIC combinations and verify a complete RocksDB build with compression, benchmark, and io_uring features.
