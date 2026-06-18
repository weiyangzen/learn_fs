# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindTSan.cmake

## Purpose

`FindTSan.cmake` provides optional ThreadSanitizer instrumentation for selected targets. It validates compatibility with MemorySanitizer, platform, and pointer width, probes compiler support, and exposes `add_sanitize_thread(TARGET)`.

## Important APIs, Types, and Functions

The main public API is function `add_sanitize_thread`. It uses option `SANITIZE_THREAD`, flag candidate `-g -fsanitize=thread`, and helper functions `sanitizer_check_compiler_flags` and `sanitizer_add_flags`.

## Control Flow

If both `SANITIZE_THREAD` and `SANITIZE_MEMORY` are enabled, configuration stops with a fatal error. When TSan is enabled, non-Linux and non-64-bit systems force the option off with warnings. Supported configurations probe TSan flags. `add_sanitize_thread` appends detected compile/link flags to the target only when enabled.

## State and Persistence Behavior

The module writes `SANITIZE_THREAD` and `TSan_<compiler>_FLAGS` cache state and mutates target properties when used.

## Dependencies and Integration Points

It depends on `sanitize-helpers.cmake`, CMake enabled language metadata, and compiler/runtime TSan support. It is used through `FindSanitizers.cmake`.

## Risks and Edge Cases

ThreadSanitizer changes runtime behavior and can conflict with low-level threading code, atomics, or unsupported libraries. As with MSan, warning messages refer to `${TARGET}` during global option validation. Mixed-language targets using different compiler IDs are rejected later by helper logic.

## Test Signals

Configure 64-bit Linux with `-DSANITIZE_THREAD=ON`, inspect flags, and run threaded unit/integration tests. Negative tests should cover `SANITIZE_MEMORY` conflict, non-Linux, and 32-bit builds.
