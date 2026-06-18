# sources/storage-engines/foundationdb/contrib/debug_determinism/CMakeLists.txt

## Purpose
Builds the `debug_determinism` static instrumentation helper library.

## Important APIs, Types, And Functions
Adds static target `debug_determinism` from `debug_determinism.cpp` and applies `-fPIC` for convenient linking into shared libraries such as `libfdb_c.so`.

## Control Flow
CMake target creation is unconditional; compile option is applied to the target.

## State And Persistence
No runtime state in this file. It changes build artifacts.

## Dependencies And Integration
The target is intended for use with a `TRACE_PC_GUARD_INSTRUMENTATION_LIB` CMake option or sanitizer coverage instrumentation.

## Risks
`-fPIC` is compiler/platform-specific and assumed accepted. No include directories or explicit linkage are declared.

## Test Signals
Configure/build with the instrumentation option and verify the static library can link into a DSO.
