# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/compiler.h

This is a Linux compiler compatibility shim used by the vendored FAT checker code.

Core contents:
- Defines sparse/checker annotations such as `__user`, `__force`, `__iomem`, and lock annotations to empty forms unless `__CHECKER__` is used.
- Under `__KERNEL__`, includes GCC-version-specific Linux compiler headers and defines branch prediction/barrier macros.
- Provides fallback definitions for `__deprecated`, `__must_check`, `__attribute_used__`, `__attribute_pure__`, `__attribute_const__`, `noinline`, and `__always_inline`.

Risk points:
- It is not a full Linux compiler header replacement.
- Several macros are intentionally “unimplemented” fallbacks.
- Kernel-mode include branches are not meaningful for this ReactOS user-mode library build.
