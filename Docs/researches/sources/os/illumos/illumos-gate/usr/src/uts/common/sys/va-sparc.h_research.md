# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va-sparc.h

## Role

Provides SPARC-specific GNU/Sun-compatible variable argument implementation definitions for old compiler/header paths.

## Key Interfaces

- Defines `__gnuc_va_list` differently for SPARC v9 and non-v9/SVR4 compatibility cases.
- For SPARC v9, `__gnuc_va_list` is a struct tracking next integer output register, floating register, limits, and stack argument pointer.
- Defines `va_start` for stdarg and varargs styles using GCC builtins such as `__builtin_saveregs`, `__builtin_args_info`, and `__builtin_next_arg`.
- Defines `va_alist`/`va_dcl` for old varargs style.
- Defines `va_end` as no-op after optional libgcc declaration.
- Defines `enum __va_type_classes` mirroring GCC type classification.
- Defines `va_arg` for SPARC v9 register/stack ABI and for non-v9 rounded-size stack access, including aggregate and long-double handling.

## Risk Notes

This header encodes ABI-specific varargs mechanics. It depends on GCC builtins and SPARC calling conventions; incorrect alignment or register/stack transition handling breaks all variadic functions on affected builds.
