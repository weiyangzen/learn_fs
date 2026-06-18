# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindUBSan.cmake

## Purpose

`FindUBSan.cmake` adds optional UndefinedBehaviorSanitizer support to selected targets.

## Important APIs, Types, and Functions

It exposes option `SANITIZE_UNDEFINED` and function `add_sanitize_undefined(TARGET)`. It delegates compiler probing and target flag mutation to `sanitize-helpers.cmake` under prefix `UBSan`.

## Control Flow

When enabled, the module probes `-g -fsanitize=undefined`. `add_sanitize_undefined` returns if disabled and otherwise appends detected UBSan compile/link flags to the target.

## State and Persistence Behavior

It writes CMake cache variables such as `SANITIZE_UNDEFINED` and `UBSan_<compiler>_FLAGS`, plus target `COMPILE_FLAGS` and `LINK_FLAGS` when applied.

## Dependencies and Integration Points

It depends on compiler UBSan support and the shared sanitizer helper module. It is invoked through `FindSanitizers.cmake` and `add_sanitizers`.

## Risks and Edge Cases

UBSan runtime behavior varies by compiler and may require additional recover/trap options that this module does not expose. It does not validate runtime library availability separately from compiler flag acceptance.

## Test Signals

Configure with `-DSANITIZE_UNDEFINED=ON`, build targets, and run tests that exercise integer, alignment, and nullability edge cases. Inspect target flags to confirm both compile and link instrumentation.
