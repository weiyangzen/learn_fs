# File Research: sources/local-fs/dlm/dlm_controld/linux_helpers.h

This header is a small userspace copy of Linux helper macros needed by local kernel-derived headers.

It defines:
- `static_assert()` wrapper around C11 `_Static_assert`.
- `__same_type()` using GCC `__builtin_types_compatible_p`.
- Poison pointers `LIST_POISON1` and `LIST_POISON2`.
- `container_of()` with type checking.
- `READ_ONCE()` and `WRITE_ONCE()` volatile access helpers.

Used by:
- `list.h`
- `rbtree.h`
- `rbtree_augmented.h`

Important detail:
- This file assumes GCC/Clang extensions: `typeof`, statement expressions, and `__builtin_types_compatible_p`.
