# sources/storage-engines/wiredtiger/cmake/platform/arch/aarch64.cmake

## Purpose
`aarch64.cmake` applies ARM64-specific compiler options for WiredTiger.

## Important APIs, Types, And Functions
It includes `CheckCCompilerFlag` and `cmake/rcpc_test.cmake`, reads `HAVE_RCPC`, calls `add_compile_options`, checks `-moutline-atomics`, and unsets the temporary cache result.

## Control Flow
If the RCpc compile test succeeds, it adds `-march=armv8.2-a+rcpc+crc`; otherwise it adds `-march=armv8-a+crc`. It then checks compiler support for `-moutline-atomics` and adds it when available.

## State And Persistence Behavior
This file mutates global compile options for the build directory. The `HAVE_RCPC` result can also flow into the generated config header.

## Dependencies And Integration Points
It depends on the RCpc probe and ARM compiler flag support. It is selected by architecture platform setup when `WT_ARCH` is aarch64.

## Risks
Forcing `-march` may conflict with user-provided CPU flags or cross-compiler defaults. `-moutline-atomics` support detection is compiler-version dependent and can affect runtime compatibility/performance.

## Test Signals
Configure native and cross aarch64 builds with and without RCpc support, inspect compile flags, and compile atomic/checksum code paths.
