# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindMSan.cmake

## Purpose

`FindMSan.cmake` adds optional MemorySanitizer support to selected targets. It exposes the `SANITIZE_MEMORY` option, validates platform constraints, probes compiler flags, and provides `add_sanitize_memory(TARGET)`.

## Important APIs, Types, and Functions

The main API is the CMake function `add_sanitize_memory`. It delegates flag probing and target mutation to `sanitizer_check_compiler_flags` and `sanitizer_add_flags` from `sanitize-helpers.cmake`.

## Control Flow

When `SANITIZE_MEMORY` is enabled, the module rejects non-Linux systems and non-64-bit builds by forcing the cache option back off. On a supported platform it checks `-g -fsanitize=memory` under the `MSan` prefix. `add_sanitize_memory` returns immediately if disabled; otherwise it appends the detected MSan flags to the target compile and link flags.

## State and Persistence Behavior

State is held in CMake cache variables such as `SANITIZE_MEMORY` and `MSan_<compiler>_FLAGS`. Target state is mutated through `COMPILE_FLAGS` and `LINK_FLAGS`.

## Dependencies and Integration Points

The module depends on `sanitize-helpers.cmake`, enabled CMake languages, and compiler support for MemorySanitizer. It is invoked indirectly by `FindSanitizers.cmake` and `add_sanitizers`.

## Risks and Edge Cases

MSan requires instrumented dependencies to avoid false positives and uninitialized data from external libraries, but the module only checks compiler flag availability. Warning messages reference `${TARGET}` during configure-time option checks even though no target is in scope. MSan is incompatible with TSan by policy in the sibling TSan module.

## Test Signals

Configure with Clang on 64-bit Linux and `-DSANITIZE_MEMORY=ON`, then verify selected targets receive `-fsanitize=memory`. Negative signals include non-Linux or 32-bit configure runs forcing the option off and mixed-compiler targets being rejected by helper logic.
