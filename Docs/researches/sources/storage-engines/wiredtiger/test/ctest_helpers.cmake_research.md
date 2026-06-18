# sources/storage-engines/wiredtiger/test/ctest_helpers.cmake

## Purpose
This file defines CMake helper functions for building WiredTiger C/C++ test executables and registering CTest tests or variants with consistent includes, libraries, runtime paths, copied assets, and labels.

## Important APIs, Types, and Functions
- `create_test_executable` creates a target, applies compiler diagnostics, include paths, linked libraries, optional output name/directory, optional copied files/directories, Darwin dSYM generation, platform RPATH, math library, Windows shim, and Antithesis voidstar linkage.
- `define_test_variants` expands `variant_name|variant args` entries into separate CTest tests with per-variant working directories and labels.
- `define_c_test` combines executable creation with CTest registration, optional exec script wrapping, dependency gating through `eval_dependency`, labels, and variants.

## Control Flow
Each function parses arguments with `cmake_parse_arguments` and emits fatal errors for unknown or missing required arguments. `create_test_executable` sets defaults, calls `add_executable`, configures target properties and platform-specific build/link behavior, then creates copy/sync custom targets for additional files/directories. `define_test_variants` creates working directories, separates variant args according to platform, and registers each test. `define_c_test` validates mutually exclusive `ARGUMENTS`/`VARIANTS`, checks dependencies, delegates executable creation, and either creates variants or a single `add_test`.

## State and Persistence Behavior
The helpers create build-system targets, copied runtime files, synced runtime directories, per-test working directories, and CTest metadata. Runtime output directories are set to current or caller-specified binary dirs.

## Dependencies and Integration Points
They depend on top-level variables and targets such as `wt::wiredtiger`, `test_util`, `COMPILER_DIAGNOSTIC_C_FLAGS`, `WT_LINUX`, `WT_DARWIN`, `WT_WIN`, `ENABLE_ANTITHESIS`, `CMAKE_SOURCE_DIR`, and `CMAKE_BINARY_DIR`. `define_c_test` integrates csuite labels `check;csuite` and supports script-based execution.

## Risks and Test Signals
Configuration-time fatal errors catch malformed helper use. In `define_c_test`, the variants path passes `CMDS ${test_cmd}` to `define_test_variants`, but the callee expects `CMD`; this looks like a potential typo that could leave custom commands unused for variants. Directory syncing is direct-child only because it delegates to `ctest_dir_sync.cmake`.
