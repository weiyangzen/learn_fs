# File Research: sources/os/bsd/freebsd-src/sys/sys/cdefs.h

## Purpose
`cdefs.h` is FreeBSD's central compiler, language, ABI, and annotation compatibility header.

## Main Interfaces
- Provides feature-test fallbacks for `__has_attribute`, `__has_extension`, `__has_feature`, `__has_include`, and `__has_builtin`.
- Defines compiler/version checks, compiler barriers, inline/volatile compatibility, stringification, token concatenation, and K&R/ANSI prototype macros.
- Declares common attributes: weak, noreturn, const/pure, unused/used, deprecated, packed, aligned, section, alloc-size, malloc-like, always-inline, noinline, warn-unused-result, format checking, visibility, and more.
- Supplies C11/C++ compatibility for `_Alignas`, `_Alignof`, `_Noreturn`, `_Static_assert`, `_Thread_local`, `_Generic`-like `__generic`, and `__min_size`.
- Defines branch prediction, `__containerof`, offsetof/range helpers, symbol references/versioning, RCS/COPYRIGHT embedding, dequalification casts, rename support, visibility settings, nullability macros, type tags, lock annotations, sanitizer opt-outs, stack protector opt-out, and alignment builtins/fallbacks.

## Implementation Notes
This header deliberately centralizes compiler-specific conditionals so the wider source tree can use stable FreeBSD macros. It handles GCC, Clang, TinyCC, C, and C++ modes with extensive fallbacks.

## Dependencies and Constraints
It errors if `_KERNEL` and `_STANDALONE` are both defined. Includes `sys/_decls.h` and `sys/_visible.h`. Some macros expand to compiler attributes only when the active compiler supports them.
