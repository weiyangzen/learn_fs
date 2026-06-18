# sources/storage-engines/wiredtiger/CMakeLists.txt

## Purpose
This is WiredTiger's top-level CMake build definition. It configures platform detection, third-party libraries, build modes, generated headers, static/shared library targets, Python/workgen bindings, test suites, benchmarks, examples, and tools.

## Important APIs, Types, and Functions
Key CMake helpers include `parse_filelist_source`, `define_wiredtiger_library`, `configure_file`, `FetchContent_Declare/MakeAvailable`, `enable_testing`, `add_subdirectory`, and `setup_gdb_autoloader`. Important variables include `WT_ARCH`, `WT_OS`, `ENABLE_STATIC`, `ENABLE_SHARED`, `WITH_PIC`, `ENABLE_PYTHON`, `HAVE_BUILTIN_EXTENSION_*`, `ENABLE_STRICT`, and `ENABLE_LLVM`.

## Control Flow
CMake detects target architecture/OS, includes platform files, sets ccache if available, loads third-party discovery and base config, enforces at least one library flavor, applies compiler standard and strict/color options, optionally fetches Catch2, parses the `dist/filelist`, builds builtin extension object lists, generates `wiredtiger.h` and `wiredtiger_config.h`, creates object/static/shared library targets, aliases `wt::wiredtiger`, then descends into utilities, install rules, Python/workgen, benchmark/test/example/tool directories.

## State, Persistence, and Dependencies
Build state is CMake cache, generated headers under the binary directory, object libraries, and install/export metadata. Dependencies include platform config modules, third-party compression/crypto/memkind/IAA/lazyfs/voidstar/sqlite discovery, Python3/SWIG for bindings, and Catch2 for unit tests.

## Integration Points, Risks, and Test Signals
This file is the central integration point for all compiled WiredTiger artifacts. Risks include feature-toggle interactions, PIC requirements for shared/SWIG consumers, typo-prone variable names, and network dependency when fetching Catch2. Signals are successful configure/generate/build across presets and the existence of expected benchmark/test targets.
