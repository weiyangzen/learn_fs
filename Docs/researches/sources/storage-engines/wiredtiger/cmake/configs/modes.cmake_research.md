# sources/storage-engines/wiredtiger/cmake/configs/modes.cmake

## Purpose
`modes.cmake` defines available WiredTiger build types and compiler/linker flags for default, sanitizer, and coverage configurations.

## Important APIs, Types, And Functions
The key function is `define_build_mode(mode ...)`, which accepts C/CXX compiler flags, link flags, libraries, and dependency expressions. It sets `BUILD_MODES`, compiler family variables (`MSVC_C_COMPILER`, `CLANG_C_COMPILER`, `GNU_C_COMPILER`, and CXX variants), and cache variables like `CMAKE_C_FLAGS_ASAN`.

## Control Flow
The file detects compiler families, defines `define_build_mode`, constructs frame-pointer, ASan, UBSan, MSan, TSan, and Coverage flags, validates compiler support using `check_c_compiler_flag` and `check_cxx_compiler_flag`, initializes cache flags once per build type, and rejects unavailable `CMAKE_BUILD_TYPE` values.

## State And Persistence Behavior
Build modes and their flags are persisted in the CMake cache. Per-mode initialization is guarded by `WT_BUILD_MODE_<MODE>_FLAGS_INITIALIZED`, preventing repeated re-seeding from overwriting user edits in the same build directory.

## Dependencies And Integration Points
It includes `CheckCCompilerFlag`, `CheckCXXCompilerFlag`, and `helpers.cmake` for dependency evaluation. `base.cmake` later depends on `BUILD_MODES` and compiler family variables for debug and optimization flag logic.

## Risks
Flag checks are only as good as the active compiler/linker environment; unsupported sanitizer libraries may still fail later at link or runtime. The file uses `MSVC` in dependency expressions even though compiler booleans are also defined separately, so CMake's own `MSVC` variable must be reliable.

## Test Signals
Configure each build type (`Debug`, `Release`, `RelWithDebInfo`, `ASan`, `UBSan`, `MSan`, `TSan`, `Coverage`) under Clang/GCC/MSVC where applicable and verify invalid build types fail at configure time.
