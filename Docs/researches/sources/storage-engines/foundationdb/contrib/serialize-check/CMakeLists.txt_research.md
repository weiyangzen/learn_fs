# sources/storage-engines/foundationdb/contrib/serialize-check/CMakeLists.txt

## Purpose
This CMake file builds the `fdb-serialize-check` utility, specifically the `source_scanner` executable used by the serialize-check tooling. The utility scans FoundationDB C++ sources with Clang LibTooling and emits JSON describing classes with FDB-style `serialize` methods.

## Important APIs, Targets, And Settings
- Requires CMake 3.24 and declares project `fdb-serialize-check` for C and C++.
- `find_package(Boost REQUIRED COMPONENTS json)` provides `Boost::json`, matching the scanner's use of `<boost/json.hpp>`.
- `set(CMAKE_CXX_STANDARD 20)` builds the C++ scanner as C++20.
- `find_package(Clang REQUIRED CONFIG)` discovers an installed Clang/LLVM package and prints `LLVM_VERSION_MAJOR`.
- `LLVM_CMAKE_MODULE_PATH` is derived from `CLANG_INCLUDE_DIRS` and appended with Clang/LLVM module paths before including `AddLLVM` and `AddClang`.
- `SOURCE_SCANNER_BINARY` points to `src/SourceScanner.cpp`.
- `add_clang_executable(source_scanner ${SOURCE_SCANNER_BINARY})` creates the tool target.
- `target_include_directories` adds Clang, LLVM, and Boost include dirs.
- `target_link_libraries` links `clangAST`, `clangASTMatchers`, `clangBasic`, `clangFrontend`, `clangSerialization`, `clangTooling`, and `Boost::json`.

## Control Flow
CMake configures dependencies first, extends the module path with Clang/LLVM helper modules, includes target-building macros, and then declares a single executable target. There are no install rules, tests, or higher-level integration hooks in this file.

## State And Persistence Behavior
This file does not manage runtime state. Build artifacts are produced in the CMake build directory, with `source_scanner` as the important output. The companion README indicates users typically copy or run `source_scanner` alongside `renormalize.py` from a FoundationDB source root with a compilation database.

## Dependencies And Integration Points
The target is tightly coupled to LLVM/Clang package layout and Boost.JSON. `renormalize.py` expects a `source_scanner` binary path, defaulting to `./source_scanner` in the current working directory. `SourceScanner.cpp` depends on the Clang libraries linked here to parse C++ translation units from a compilation database.

## Risks And Edge Cases
- Deriving `LLVM_CMAKE_MODULE_PATH` from `${CLANG_INCLUDE_DIRS}/../lib/cmake` is package-layout-sensitive and may fail on distributions where Clang CMake modules are not adjacent to include directories.
- The file assumes imported target `Boost::json` exists, which depends on the Boost CMake package/version.
- There is no version pin despite README examples referencing LLVM/libtooling behavior; scanner source comments mention differences around LLVM 15/16.
- No install target means downstream scripts may fail if they assume the binary is in the repository root rather than the build tree.
- No tests are declared here, so build success is the only direct validation at CMake level.

## Test Signals
Primary validation is configuring with Clang and Boost.JSON installed, then building `source_scanner`. A stronger smoke test would run the binary on a small C++ file with a compilation database and verify JSON lines are emitted. CI should also exercise at least one Clang/LLVM version supported by the scanner source.
