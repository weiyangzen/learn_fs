# sources/storage-engines/rocksdb/build_tools/fbcode_config.sh research

Purpose: `fbcode_config.sh` prepares environment variables for building RocksDB with Meta internal fbcode toolchains and dependency paths. It targets an older non-platform010 layout and is intended to be sourced by build scripts.

Important APIs: the script exports compiler variables `CC`, `CXX`, `AR`, flags `CFLAGS`, `CXXFLAGS`, `EXEC_LDFLAGS`, `EXEC_LDFLAGS_SHARED`, dependency-specific include/lib variables, `VALGRIND_VER`, `JEMALLOC_LIB`, `JEMALLOC_INCLUDE`, `CLANG_ANALYZER`, and `CLANG_SCAN_BUILD`. Behavior is controlled by `PIC_BUILD`, `USE_CLANG`, `ROCKSDB_DISABLE_*`, `USE_SSE`, and `PORTABLE`.

Control flow: it derives `BASEDIR`, sources `dependencies.sh`, builds include/lib variables for libgcc, glibc, compression libraries, gflags, jemalloc, numa, libunwind, and TBB, sets default portability/SSE options, selects GCC or Clang toolchain branches, appends RocksDB feature macros, constructs linker flags including dynamic linker/rpath, and exports the resulting environment.

State and persistence: it mutates only the current shell environment when sourced. It does not write files.

Dependencies and integration: it assumes Meta third-party dependency variables from `dependencies.sh`. It is consumed by internal build flows and older scripts such as `fb_compile_mongo.sh`.

Risks and test signals: this file is highly environment-specific and appears fragile: the `CLANG_SCAN_BUILD` assignment is missing a closing quote in the viewed source, which can break sourcing. It also uses `$BASH_SOURCE` while declaring `/bin/sh`, and many unquoted variables. Test signals are successful sourcing in both GCC and Clang modes and successful RocksDB internal builds.
