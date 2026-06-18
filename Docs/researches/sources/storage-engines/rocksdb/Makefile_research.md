# sources/storage-engines/rocksdb/Makefile

## Purpose
`Makefile` is RocksDB's hand-written GNU make build, test, packaging, install, JNI, and developer-maintenance orchestrator. It builds static and shared RocksDB libraries, tools, benchmarks, hundreds of test executables, Java JNI artifacts, downloaded static compression dependencies for JNI packages, generated build metadata, dependency files, amalgamated sources, package metadata, and multiple CI-oriented validation flows.

Compared with the CMake file, this Makefile owns more developer workflow: debug-level defaults, shared/static mode selection, ccache wrapping, git hook setup, parallel test sharding through GNU parallel, sanitizer and valgrind targets, source/header formatting checks, source-list validation, Docker/Vagrant Java release builds, and cleanup of generated artifacts.

## Important APIs, variables, rules, and targets
- Included build fragments are `common.mk`, generated `make_config.mk`, `src.mk`, plugin makefiles under `plugin/<plugin>/*.mk`, `folly.mk`, and `crash_test.mk`.
- User-facing configuration variables include `DEBUG_LEVEL`, `OBJ_DIR`, `LIB_MODE`, `EXTRA_CFLAGS`, `EXTRA_CXXFLAGS`, `EXTRA_LDFLAGS`, `EXTRA_ARFLAGS`, `MACHINE`, `ROCKSDB_CXX_STANDARD`, `USE_COROUTINES`, `USE_FOLLY`, `USE_FOLLY_LITE`, `USE_CLANG`, `PORTABLE`, `ROCKSDB_NO_FBCODE`, `USE_CCACHE`, `USE_LTO`, `COERCE_CONTEXT_SWITCH`, sanitizer flags, `ASSERT_STATUS_CHECKED`, `DISABLE_WARNING_AS_ERROR`, `ROCKSDB_PLUGINS`, `ROCKSDBTESTS_SUBSET`, `J`, `GTEST_SHARD_SIZE`, `NCORES`, `PREFIX`, `LIBDIR`, `DESTDIR`, `JAVA_HOME`, and Java release-version variables.
- Generated configuration is created by `build_tools/build_detect_platform`, which writes `make_config.mk`. The Makefile then includes it to obtain platform flags, source lists, compiler choices, shared-library names, compression/allocator findings, and OS-specific settings.
- Main library outputs are `STATIC_LIBRARY`, `STATIC_TEST_LIBRARY`, `STATIC_TOOLS_LIBRARY`, `STATIC_STRESS_LIBRARY`, shared version/symlink outputs `SHARED1` through `SHARED4`, and derived `LIBRARY`, `TEST_LIBRARY`, `TOOLS_LIBRARY`, and `STRESS_LIBRARY`.
- Primary targets include `all`, `all_but_some_tests`, `static_lib`, `shared_lib`, `stress_lib`, `tools`, `tools_lib`, `test_libs`, `benchmarks`, `microbench`, `run_microbench`, `dbg`, `release`, `coverage`, `check`, `check_some`, `valgrind_check`, `asan_check`, `ubsan_check`, `analyze`, `clean`, `format`, `format-auto`, `check-format`, `check-buck-targets`, `check-sources`, `check-workflow-yaml`, `clang-tidy`, `package`, `install`, `install-static`, `install-shared`, `uninstall`, and `gen-pc`.
- Pattern rules compile `$(OBJ_DIR)/%.o` from `.cc`, `.cpp`, and `.c`; iOS has special `.cc.o` and `.c.o` universal-object recipes. Dependency rules generate `$(OBJ_DIR)/%.cc.d`, `$(OBJ_DIR)/%.cpp.d`, and PowerPC-specific `.c.d`/`.S.d` files with compiler `-MM`.
- Generated source and metadata targets include `util/build_version.cc`, `unity.cc`, `unity.a`, `rocksdb.h`, `rocksdb.cc`, and `rocksdb.pc`.
- JNI/package targets include `rocksdbjava`, `rocksdbjavastatic`, `rocksdbjavastaticosx`, `rocksdbjavastaticosx_ub`, `rocksdbjavastaticrelease`, `rocksdbjavastaticreleasedocker`, many `rocksdbjavastaticdocker*` cross-build targets, `rocksdbjavastaticpublishcentral`, `rocksdbjavastaticnexusbundlejar`, Java source/javadoc jars, `jclean`, `jtest`, `jpmd`, and `jdb_bench`.

## Control flow
The Makefile starts by selecting bash as the shell, importing `common.mk`, initializing flags, and deriving `DEBUG_LEVEL`, `OBJ_DIR`, and `LIB_MODE` from requested goals. Production and install-style goals force `DEBUG_LEVEL=0`; `dbg` forces `DEBUG_LEVEL=2`; shared/static install goals choose matching library modes; Java static goals use separate object directories (`jl` or `jls`) and usually force release optimization.

Before most variables are finalized, a shell call exports key settings and invokes `build_tools/build_detect_platform "$(CURDIR)/make_config.mk"`. The generated `make_config.mk` is immediately included, making platform detection a required configure step for almost every invocation. The Makefile then layers optimization flags, frame-pointer settings, architecture feature tests, shared-library flags, coroutine/Folly behavior, sanitizer behavior, jemalloc decisions, gtest include flags, warning policy, plugin flags, source/object lists, test lists, and library names.

Default target resolution points `default` to `all`. `all` first runs `setup-hooks`, then builds the selected library, benchmarks, tools, tools library, test libraries, and all tests. `release` cleans and rebuilds the library, tools, and `db_bench` with `DEBUG_LEVEL=0`. `dbg` builds the library, benchmarks, tools, and tests under debug-level-2 semantics.

Library construction is split by mode. Static archives are created from object lists with `$(AR) $(ARFLAGS)`. Shared libraries use platform shared linker flags and, on versioned platforms, build the most specific shared object (`SHARED4`) and create symlinks for major/minor/unversioned names. Test/tools/stress libraries are similarly archived or shared-linked from their object subsets.

Executable construction is mostly explicit. A small `MakeTestRule` macro handles plugin tests, but the majority of tests, tools, and benchmarks have individual targets linking specific object files with `$(TEST_LIBRARY)`, `$(TOOLS_LIBRARY)`, `$(STRESS_LIBRARY)`, and `$(LIBRARY)`. This gives precise per-binary dependencies but makes the file long and source-list drift-prone.

The `check` target builds `all`, cleans stale test temp directories, generates sharded test runner scripts under `t/run-*`, and uses `build_tools/gnu_parallel` when available and `J != 1`; otherwise it runs test binaries sequentially. Parallel flow enumerates gtest cases with `--gtest_list_tests`, computes per-binary shard counts from `GTEST_SHARD_SIZE` and `NCORES`, applies overrides for slow binaries, supports CI shard partitioning, writes one shell script per shard, prioritizes historically slow tests, captures logs in `LOG` and `t/log-*`, and post-processes the GNU parallel joblog for failures. After C++ tests it runs Python/tool checks and formatting/source/workflow validation unless skipped.

The Java path derives JNI output names by OS, CPU, bitness, and libc. Dynamic `rocksdbjava` builds Java classes, links a JNI shared object from native JNI sources plus RocksDB objects, jars classes plus the native library, and writes SHA1 metadata. Static Java builds first download and checksum zlib, bzip2, snappy, lz4, and zstd sources, build static archives, compile RocksDB objects with compression macros and include paths, link a self-contained JNI library, and package platform-specific and all-platform jars.

Install flow generates `rocksdb.pc`, installs headers and plugin headers under `$(PREFIX)/include/rocksdb`, installs static or shared libraries under `$(LIBDIR)`, writes pkg-config metadata, and creates shared-library symlinks. `uninstall` removes the same installed include tree, libraries, symlinks, and pkg-config file.

## State and persistence behavior
The Makefile writes several source-tree artifacts during normal operation. `make_config.mk` is generated in the source directory and included by later make phases. `util/build_version.cc` is regenerated unless `NO_UPDATE_BUILD_VERSION` is set; it embeds Git SHA, branch/tag, dirty status, build date, Git date, RocksDB version, and plugin registration strings. `rocksdb.pc`, `unity.cc`, `rocksdb.h`, `rocksdb.cc`, dependency files, object files, archives, shared libraries, test binaries, logs, temp test directories, and Java `target/` artifacts are also created under the source tree by default.

Test execution persists `LOG`, per-shard/per-test files under `t/`, and temp directories under `$(TEST_TMPDIR)`. The `check` target removes stale temp directories older than three hours before running and removes `$(TEST_TMPDIR)` at the end. `watch-log`, `dump-log`, `suggest-slow-tests`, and `check-progress` consume these outputs for monitoring.

Dependency tracking persists `.d` files under `$(OBJ_DIR)` and conditionally includes them unless the requested goals are cleanup/format/static-analysis style commands. Java static dependency builds persist downloaded tarballs, extracted third-party source directories, and static archives (`libz.a`, `libbz2.a`, `libsnappy.a`, `liblz4.a`, `libzstd.a`) until cleaned.

`setup-hooks` mutates repository-local Git config by setting `core.hooksPath=githooks` on first build when `.git` and `githooks` exist. `install-hooks` and `uninstall-hooks` can also copy/remove hook files under `.git/hooks`.

## Dependencies and integration points
The Makefile depends heavily on repository-local scripts and fragments: `common.mk`, `src.mk`, `folly.mk`, `crash_test.mk`, `build_tools/build_detect_platform`, `build_tools/gnu_parallel`, `build_tools/check_progress.sh`, `build_tools/check-public-header.sh`, `build_tools/format-diff.sh`, `build_tools/check-sources.sh`, `build_tools/check-workflow-yaml.sh`, `build_tools/version.sh`, `build_tools/amalgamate.py`, `build_tools/make_package.sh`, `tools/run_clang_tidy.py`, `tools/check_all_python.py`, `tools/ldb_test.py`, `tools/db_crashtest_test.py`, `tools/rocksdb_dump_test.sh`, and Java sub-Makefiles.

External tool dependencies include bash, Perl, awk, sed, grep, find, git, ctags, cscope, GNU parallel or the vendored wrapper, valgrind, clang scan-build/analyzer, clang-tidy, Python, curl, tar, cmake for Snappy static dependency builds, Docker, Vagrant, Maven, GPG, OpenSSL, Java `jar`, and platform-specific tools such as `lipo`, `xcrun`, `xcode-select`, `getconf`, and checksum commands.

External library integration includes jemalloc, Folly, gflags through plugin/pkg-config paths, sanitizer runtimes, static compression libraries for Java packaging, and platform shared-library support. Plugin integration imports `plugin/<name>/*.mk`, appends plugin sources, headers, libraries, link flags, JNI native sources, Java include flags, pkg-config requirements, plugin tests, and built-in registry function declarations.

Build outputs integrate with downstream C/C++ consumers through static/shared RocksDB libraries, installed headers, pkg-config metadata, generated amalgamated C/C++ files, and Java consumers through platform-specific `rocksdbjni` jars.

## Risks and edge cases
- `build_tools/build_detect_platform` runs during makefile evaluation and writes `make_config.mk`. If platform detection is slow, non-hermetic, or wrong, every target inherits the result. A failed or stale `make_config.mk` can break unrelated maintenance goals.
- The build writes many generated files into the source tree, including `util/build_version.cc`; interrupted builds or concurrent invocations can leave inconsistent generated state.
- `setup-hooks` changes Git config as part of `all`, so a normal build has repository side effects outside compiler outputs.
- Goal-dependent mutation of `DEBUG_LEVEL`, `LIB_MODE`, and `OBJ_DIR` can surprise users combining goals in one invocation. Java static, install, debug, and release targets alter optimization and linkage expectations.
- The manual executable rule list is very large. Source-list or test-list changes can easily update `src.mk` without adding the matching target, or leave stale explicit targets.
- Parallel test sharding generates shell scripts from test binary names and relies on gtest list output shape. Badly behaved test listing, non-gtest binaries, CI shard variables, or missing GNU parallel can change behavior significantly.
- The test prioritization regex and shard-size overrides are empirical. If test timing changes, slow tests may be scheduled poorly until `suggest-slow-tests` is rerun and the regex is updated.
- Sanitizer flows disable jemalloc and add global flags, but they also run broad clean/rebuild/test cycles. Combining sanitizer variables with custom flags or shared builds can produce difficult linker/runtime failures.
- Java static dependency targets download third-party tarballs over the network and verify hardcoded hashes. Network failures, upstream URL changes, missing TLS support, or changed archives will break Java package builds.
- Install/uninstall recipes remove broad include/library paths under the selected prefix. Incorrect `DESTDIR`, `PREFIX`, or `LIBDIR` values can affect system paths.
- Several platform sections assume GNU-ish tools or specific OS command behavior. AIX, OpenBSD, macOS universal builds, musl detection, and cross-Docker flows need separate validation.

## Test signals
Core build validation should include `make static_lib`, `make shared_lib`, `make all_but_some_tests ROCKSDBTESTS_SUBSET=<small subset>`, `make tools`, `make db_bench`, and `make clean`. Debug/release behavior should be checked through `make dbg`, `make release`, and explicit `DEBUG_LEVEL=0` production builds.

Test validation should include `make check J=1` for sequential behavior, `make check` with GNU parallel available for sharding behavior, `make check_some ROCKSDBTESTS_SUBSET="db_basic_test env_basic_test"` for subset selection, `make suggest-slow-tests` after a check run, and `make check-progress` while tests are running. Header and source hygiene signals are `make check-headers`, `make check-format`, `make check-sources`, `make check-buck-targets`, and `make check-workflow-yaml`.

Runtime-analysis signals include `make asan_check`, `make ubsan_check`, `make valgrind_check`, and representative crash-test targets from `crash_test.mk`. Packaging/install signals include `make gen-pc`, `make install-static DESTDIR=<staging>`, `make install-shared DESTDIR=<staging>`, `make uninstall DESTDIR=<staging>`, and inspection of generated `rocksdb.pc`.

JNI signals include `make rocksdbjava JAVA_HOME=<jdk>`, `make jtest`, `make rocksdbjavastatic JAVA_HOME=<jdk>`, checksum failure tests for downloaded dependency tarballs, and platform-specific static release builds only in environments with the required Docker/Vagrant tooling.
