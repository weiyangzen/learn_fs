# sources/test-tools/stress-ng/core-version.h

## Purpose
`core-version.h` provides preprocessor helpers for comparing libc and compiler versions.

## Important APIs, Types, And Functions
`STRESS_VERSION_NUMBER` packs major, minor, and patchlevel into a comparable integer. `NEED_GLIBC`, `NEED_GNUC`, `EQUAL_GNUC`, `NEED_CLANG`, `NEED_ICC`, and `NEED_ICX` evaluate whether the active toolchain/runtime meets a requested version, or return 0 when version macros are unavailable.

## Control Flow
The file is entirely compile-time logic. Include sites use these macros to conditionally enable code paths, work around compiler bugs, or require minimum library versions.

## State And Persistence
No runtime state exists. The persistent effect is which code gets compiled for a given build environment.

## Dependencies And Integration Points
It depends on predefined compiler/libc macros such as `__GLIBC__`, `__GNUC__`, `__clang_major__`, `__INTEL_COMPILER`, and Intel LLVM macros. It integrates with portability gates throughout stress-ng.

## Risks
Version packing assumes minor and patch values fit the two-digit fields well enough for intended comparisons. The `NEED_ICX` macro compares packed requested versions against Intel's compiler version integer directly, which may not have the same encoding as `STRESS_VERSION_NUMBER`. Missing macros resolve to 0 and can silently disable code.

## Test Signals
Build matrix coverage across GCC, Clang, glibc, musl, and Intel compilers is the primary signal. Mis-gates appear as compile failures or missing optimized paths.
