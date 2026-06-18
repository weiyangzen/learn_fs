# sources/storage-engines/rocksdb/CMakeLists.txt

## Purpose
`CMakeLists.txt` is the CMake entry point for building RocksDB as an embeddable C++20 key-value storage library. It configures platform/compiler behavior, optional compression and allocator dependencies, source aggregation for the core library, plugin integration, build-version generation, static/shared library targets, CMake package installation, JNI delegation, test targets, benchmark tools, trace tools, examples, and microbenchmarks.

The file is intended to support both Windows/MSVC and Unix-like builds. Its opening comments document a Windows Visual Studio workflow and a simpler Linux workflow, but the script itself also contains explicit handling for Apple cross-compilation, MinGW, Cygwin, FreeBSD-family systems, Android, Solaris, AIX-adjacent architecture cases, ARM64, PowerPC, s390x, and loongarch64.

## Important APIs, types, functions, and targets
- CMake module entry points: `include(ReadVersion)`, `include(GoogleTest)`, `get_rocksdb_version(rocksdb_VERSION)`, `include(CMakeDependentOption)`, `include(CheckCCompilerFlag)`, `include(CheckCXXSourceCompiles)`, `include(CheckCXXSymbolExists)`, `include(GNUInstallDirs)`, and `include(CMakePackageConfigHelpers)`.
- Major build options include `WITH_JEMALLOC`, `WITH_LIBURING`, `WITH_SNAPPY`, `WITH_LZ4`, `WITH_ZLIB`, `WITH_ZSTD`, `WITH_WINDOWS_UTF8_FILENAMES`, `ROCKSDB_BUILD_SHARED`, `WITH_GFLAGS`, `WITH_XPRESS`, `ROCKSDB_SKIP_THIRDPARTY`, `WITH_MD_LIBRARY`, `WIN_CI`, `PORTABLE`, `WITH_IOSTATS_CONTEXT`, `WITH_PERF_CONTEXT`, `FAIL_ON_WARNINGS`, `WITH_ASAN`, `WITH_TSAN`, `WITH_UBSAN`, `WITH_NUMA`, `WITH_TBB`, `DISABLE_STALL_NOTIF`, `WITH_DYNAMIC_EXTENSION`, `ASSERT_STATUS_CHECKED`, `USE_RTTI`, `OPTDBG`, `WITH_RUNTIME_DEBUG`, `WITH_FALLOCATE`, `WITH_JNI`, `WITH_TESTS`, `WITH_BENCHMARK_TOOLS`, `WITH_CORE_TOOLS`, `WITH_TOOLS`, `WITH_ALL_TESTS`, `WITH_TRACE_TOOLS`, `WITH_EXAMPLES`, and `WITH_BENCHMARK`.
- Main library targets are `rocksdb${ARTIFACT_SUFFIX}` as a static library and `rocksdb-shared${ARTIFACT_SUFFIX}` as a shared library. `ROCKSDB_LIB` is selected as the shared library on non-Windows when shared builds are enabled, otherwise the static library is used.
- Generated source state is `BUILD_VERSION_CC`, produced by `configure_file(util/build_version.cc.in ${CMAKE_BINARY_DIR}/build_version.cc @ONLY)` after collecting Git SHA, modification status, commit date, branch/tag, and build timestamp.
- Test infrastructure creates `testharness`, `testutillib${ARTIFACT_SUFFIX}`, individual test executables from `TESTS`, a `rocksdb_check` custom target, CTest registration through `gtest_discover_tests`, and a special `c_test` target for the C API when linkable.
- Tool targets include benchmark executables such as `db_bench`, `cache_bench`, `memtablerep_bench`, `range_del_aggregator_bench`, `table_reader_bench`, `filter_bench`, `hash_table_bench`, and `point_lock_bench`, trace tools such as `block_cache_trace_analyzer` and `trace_analyzer`, plus subdirectory-driven `core_tools` and `tools`.
- Install/package API includes `configure_package_config_file`, `write_basic_package_version_file`, `configure_file(${PROJECT_NAME}.pc.in ...)`, `install(TARGETS ...)`, exported `RocksDBTargets`, CMake package files under `${CMAKE_INSTALL_LIBDIR}/cmake/rocksdb`, installed public headers, plugin headers, and a `rocksdb.pc` pkg-config file.

## Control flow
Configuration starts by discovering the RocksDB version and choosing a build type. A Git checkout defaults to `Debug`; a source archive defaults to `RelWithDebInfo`. If `ccache` is available, C and C++ compiler launchers are set to `ccache`.

The next phase resolves third-party feature flags. On MSVC, gflags and XPRESS are Windows-specific options and `thirdparty.inc` is included unless skipped. On non-MSVC platforms, the script conditionally finds `JeMalloc`, `gflags`, `Snappy`, `ZLIB`, `BZip2`, `lz4`, and `zstd`; successful options add compile definitions and append imported targets or library names to `THIRDPARTY_LIBS`. Liburing, NUMA, TBB, and sanitizer options are handled later through the same pattern.

Compiler and CPU tuning is then layered on. MSVC gets warning, debug-info, runtime-library, and release flags. Other compilers get warning flags, pthread, frame-pointer preservation outside Debug, optional leaf-frame-pointer omission, and architecture-specific checks for PowerPC, ARM64 CRC/crypto, s390x, and loongarch64. `PORTABLE` controls whether the build targets a baseline CPU, the current CPU (`-march=native` or `/arch:AVX2`), or a named architecture. Feature probes add defines for atomic-library requirements, fallocate, sync-file-range, pthread adaptive mutexes, malloc usable size, sched CPU, auxv, and fullfsync.

The Folly/coroutine branch is a major fork. `USE_COROUTINES` requires that neither `USE_FOLLY` nor `USE_FOLLY_LITE` was explicitly chosen, enables C++20 coroutine flags, and then enables Folly. `USE_FOLLY` forbids shared RocksDB libraries, resolves Folly via `find_package` or `third-party/folly` getdeps output, patches gflags linkage when necessary, constructs an imported config for getdeps glog if CMake metadata is missing, explicitly links gflags when requested, and adds `Folly::folly` plus linker flags. `USE_FOLLY_LITE` instead adds selected Folly source files directly and discovers boost/fmt/glog paths from getdeps.

After environment setup, the file declares the full `SOURCES` list for core RocksDB. It appends transaction range-locking sources, plugin sources, architecture-specific CRC sources, Windows or POSIX port sources, and optional Folly-lite sources. Plugin support is handled twice: first through `add_subdirectory("plugin/${plugin}")` and plugin variables such as `${plugin}_SOURCES`, `${plugin}_TESTS`, include paths, libraries, and link paths; then through direct parsing of each `plugin/<name>/<name>.mk` to populate plugin builtins/external function declarations and extra libraries for `build_version.cc`.

Target generation creates the static library unconditionally, then the shared library if `ROCKSDB_BUILD_SHARED` is enabled. Both targets include `include/` for build consumers and link private third-party and system libraries. Shared-library properties differ on Windows and Unix-like systems: Windows sets export definitions and PDB flags under MSVC, while non-Windows sets linker language, `VERSION`, `SOVERSION`, and output name.

The final phases are optional surfaces. JNI delegates into the `java` subdirectory. Install rules are enabled on non-Windows by default and optionally on Windows. Tests and benchmarks add gtest, helper libraries, executable targets, and CTest registrations. Tools, examples, and microbenchmarks are delegated through subdirectories or explicit executable definitions.

## State and persistence behavior
The CMake script writes build-system state into the build directory rather than the source tree for normal CMake flows. Persistent configured artifacts include `${CMAKE_BINARY_DIR}/build_version.cc`, `RocksDBConfig.cmake`, `RocksDBConfigVersion.cmake`, and `rocksdb.pc`. The generated build-version source embeds Git SHA, branch/tag, dirty status, Git date, build date, and plugin registry metadata, making binaries self-describing through compiled strings.

The install phase persists public headers, plugin headers, static/shared libraries, CMake package exports, CMake helper modules, and pkg-config metadata into the install prefix. On Linux, if the install prefix is still CMake's default, the script changes it to `/usr`.

CTest registration is generated into the build tree. `rocksdb_check` is a custom target that invokes `${CMAKE_CTEST_COMMAND}` and depends on discovered test executables, except `db_sanity_test` is intentionally excluded from discovery.

## Dependencies and integration points
This file depends on repository-local CMake modules under `cmake/modules`, version headers parsed by `ReadVersion`, vendored gtest under `third-party/gtest-1.8.1/fused-src`, optional Java build logic under `java`, tool subdirectories under `tools`, `db_stress_tool`, `examples`, and `microbench`, and source inventory kept directly in the CMake file.

External dependencies are selected by options and platform: Threads is always required; optional dependencies include jemalloc, liburing, gflags, Snappy, zlib, bzip2, lz4, zstd, NUMA, TBB, Folly, glog, boost, fmt, and Windows XPRESS support. On Linux the script opportunistically uses `lld` when the compiler accepts `-fuse-ld=lld`.

The script integrates tightly with RocksDB's runtime feature macros. Build options become C/C++ definitions such as `ROCKSDB_JEMALLOC`, `JEMALLOC_NO_DEMANGLE`, `GFLAGS=1`, `SNAPPY`, `ZLIB`, `BZIP2`, `LZ4`, `ZSTD`, `ROCKSDB_IOURING_PRESENT`, `NIOSTATS_CONTEXT`, `NPERF_CONTEXT`, `ROCKSDB_DISABLE_STALL_NOTIFICATION`, `ROCKSDB_NO_DYNAMIC_EXTENSION`, `ROCKSDB_ASSERT_STATUS_CHECKED`, OS macros, `ROCKSDB_PLATFORM_POSIX`, and `ROCKSDB_LIB_IO_POSIX`.

## Risks and edge cases
- The source list is manually maintained and very large. Missing additions can silently exclude implementation files from CMake builds while Makefile or other build systems still work.
- The plugin path mixes CMake variables, `add_subdirectory`, and regex parsing of plugin makefiles. Divergence between plugin CMake metadata and plugin `.mk` content can affect source inclusion, link libraries, or build-version registration.
- `USE_FOLLY` disables shared library builds and mutates the cache state. Consumers expecting shared RocksDB artifacts can be surprised when Folly is enabled.
- The getdeps Folly fallback shells out through `exec_program`, assumes `python3`, `ls`, and `sed`, patches `folly-targets.cmake` in place, and hardcodes a Boost CMake version directory. This is brittle across getdeps layout changes.
- CPU tuning defaults to current-CPU optimization when `PORTABLE` is false. That improves local performance but can produce binaries that fail on older CPUs if packagers forget to set `PORTABLE=1` or an explicit baseline.
- `FAIL_ON_WARNINGS` defaults to ON. New compiler versions or platform headers can turn warnings into configure/build failures.
- Sanitizer options explicitly conflict with jemalloc through fatal messages, but the message command uses `message(FATAL ...)` rather than the more common `FATAL_ERROR`; this should be checked if changing sanitizer handling.
- Several compile probes include Linux-specific headers or functions. They are guarded partly by options and platform tests, but cross-compilation and unusual sysroots can still produce false negatives or unexpected flags.
- Test builds are excluded from Release through `CMAKE_DEPENDENT_OPTION`; developers may think `WITH_TESTS=ON` is enough without noticing the build-type condition.

## Test signals
Useful validation signals include `cmake -S sources/storage-engines/rocksdb -B build -DCMAKE_BUILD_TYPE=Debug`, `cmake --build build --target rocksdb`, `cmake --build build --target rocksdb-shared` when shared builds are enabled, and `cmake --build build --target rocksdb_check` followed by CTest output. Option coverage should include compression toggles (`WITH_SNAPPY`, `WITH_ZLIB`, `WITH_LZ4`, `WITH_ZSTD`, `WITH_BZ2`), `PORTABLE=1`, sanitizer builds, `WITH_TESTS`, `WITH_ALL_TESTS=OFF`, `WITH_BENCHMARK_TOOLS`, `WITH_TOOLS`, and install packaging through `cmake --install`.

Platform-specific signals should include at least one MSVC generation path with `thirdparty.inc`, one Linux build with and without `lld`, one portable package build, and one plugin-enabled build to exercise both plugin source inclusion and build-version plugin registration.
