# File Research: sources/os/bsd/dragonflybsd/sys/sys/cdefs.h

Core compiler, language, visibility, attribute, and feature-test macro header used across DragonFly kernel and userland headers.

Key responsibilities:
- Defines compiler feature probes such as `__has_attribute`, `__has_builtin`, and `__GNUC_PREREQ__`.
- Provides C/C++ declaration guards, public/hidden symbol visibility macros, and DSO visibility attributes.
- Defines token concatenation/stringification, ANSI compatibility shims, inline/const/volatile handling, and cache-line alignment helpers.
- Wraps GCC/Clang attributes for noreturn, const/pure, malloc-like, packed, aligned, section, nonnull, used, warn-unused-result, alloc-size, alloc-align, constructor, aliasing, weak references, and format checking.
- Defines `__offsetof`, `__containerof`, dequalification helpers, branch prediction macros, and C11 compatibility macros for `_Alignas`, `_Alignof`, `_Noreturn`, `_Static_assert`, `_Thread_local`, and `__generic`.
- Implements POSIX/XSI/BSD/ISO C visibility feature-test macro policy.
- Defines `__GLOBL` assembly-global helper for preserving kernel module sections.

Dependencies:
- Assumes compiler predefined macros and DragonFly integer typedefs from surrounding headers.

Notable risks:
- This file controls namespace exposure for virtually every public header; small changes can break both kernel and userland builds.
- It encodes old compiler compatibility paths alongside modern C11/C++11 behavior.
- The visibility and declaration macros are especially sensitive in C++ consumers.
