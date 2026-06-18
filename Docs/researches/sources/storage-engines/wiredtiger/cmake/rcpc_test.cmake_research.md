# sources/storage-engines/wiredtiger/cmake/rcpc_test.cmake

## Purpose
`rcpc_test.cmake` probes whether an ARM compiler/target supports RCpc load-acquire instructions.

## Important APIs, Types, And Functions
It includes `CheckCSourceCompiles`, defines `rcpc_test`, sets `CMAKE_REQUIRED_FLAGS` to `-march=armv8.2-a+rcpc+crc`, and calls `check_c_source_compiles` with an inline `ldapr` assembly snippet, setting `HAVE_RCPC`.

## Control Flow
The function-scoped test avoids leaking required flags. It compiles the snippet and treats switch-conflict warnings as failures via `FAIL_REGEX`. After calling the function, it emits a debug message when `HAVE_RCPC` is true.

## State And Persistence Behavior
The probe writes `HAVE_RCPC` into the CMake cache/check state, which architecture setup and generated headers consume.

## Dependencies And Integration Points
It is included by `platform/arch/aarch64.cmake`, which chooses ARM compile options based on the result.

## Risks
Inline assembly syntax and `-march` flag behavior are compiler-specific. User-provided CPU flags can conflict with the probe, which is why failure regex handling matters.

## Test Signals
Configure aarch64 builds with compilers/targets that support and do not support RCpc; verify `HAVE_RCPC` and selected `-march` flags.
