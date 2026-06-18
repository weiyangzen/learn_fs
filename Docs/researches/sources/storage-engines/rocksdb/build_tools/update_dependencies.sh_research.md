# sources/storage-engines/rocksdb/build_tools/update_dependencies.sh

## Purpose
This shell script generates `dependencies_platform010.sh` from Meta internal `third-party2` library locations. It captures concrete compiler and library base paths for a platform010/centos8-native RocksDB build environment.

## Important APIs, functions, and control flow
The script sets `BASEDIR=$(dirname $0)`, `TP2_LATEST=/data/users/$USER/fbsource/fbcode/third-party2/`, and writes to `$BASEDIR/dependencies_platform010.sh`. `log_header()` writes a copyright and generated-file note. `log_variable()` appends `NAME=value` for a shell variable using indirect expansion. `get_lib_base(lib, version, platform)` locates a library under third-party2: it chooses latest version when `LATEST` or blank, chooses latest `gcc-*[^fb]` platform when no platform is passed, resolves the first leaf directory with `readlink -f`, converts the library name to an uppercase `_BASE` variable name, assigns it with `eval`, and logs it.

The main body deletes/recreates the output file, logs compiler bases for GCC 11.x and llvm-fb 15, then logs bases for libgcc, glibc, snappy, zlib, bzip2, lz4, zstd, gflags, jemalloc, numa, libunwind, tbb, liburing, benchmark, kernel headers, binutils, and Valgrind. It ends with `git diff $OUTPUT`.

## State, persistence, and dependencies
The generated state is a shell fragment under `build_tools/dependencies_platform010.sh`. It depends on internal Meta filesystem layout, GNU `ls -v`, `readlink -f`, Bash features despite the shebang being `/bin/sh`, and a git checkout for the final diff. It mutates only the generated dependency file.

## Integration points
The generated dependency file is likely sourced by RocksDB internal build scripts that need fixed third-party roots. The variables form a contract: `GCC_BASE`, `CLANG_BASE`, `LIBGCC_BASE`, `GLIBC_BASE`, `SNAPPY_BASE`, and similar uppercase names.

## Risks and test signals
The `/bin/sh` shebang is risky because the script uses Bash-only `function`, `${var^^}`, and indirect expansion. The `eval` assignment is sensitive to whitespace or unusual path characters, and `ls | head` silently chooses arbitrary first matches if the tree shape changes. Test by running under Bash in the internal environment, confirming the generated shell fragment sources cleanly, reviewing `git diff`, and building an internal platform010 RocksDB target using the produced paths.
