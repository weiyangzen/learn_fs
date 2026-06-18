# File Research: sources/virtualization/spdk/lib/util/math.c

This file implements integer floor-log2 helpers.

`spdk_u32log2()` returns `31 - __builtin_clz(x)` for nonzero 32-bit values, and returns zero for input zero because log zero is undefined. `spdk_u64log2()` does the same for 64-bit values using `__builtin_clzll()`.

On GCC 6+ x86 ELF non-Clang builds, both functions use `target_clones("bmi", "arch=core2", "arch=atom", "default")` so GCC can emit multiple architecture-specific implementations.

The functions rely on static assertions that `uint32_t` matches `unsigned int` and `uint64_t` matches `unsigned long long` for the selected builtins.
