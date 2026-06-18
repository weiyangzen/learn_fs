# File Research: sources/local-fs/btrfs-progs/kernel-lib/overflow.h

## Purpose
Linux-style integer overflow and allocation-size helper macros for userspace builds.

## Key Interfaces
- Type property macros: `is_signed_type`, `type_min`, `type_max`, `is_negative`, `is_non_negative`.
- `__must_check` support through `__must_check_overflow()`.
- Arithmetic checks: `check_add_overflow`, `check_sub_overflow`, `check_mul_overflow`, `check_shl_overflow`.
- Saturating size helpers: `size_mul`, `size_add`, `size_sub`, `array_size`, `array3_size`, `flex_array_size`, `struct_size`.

## Dependencies
Includes `<stdbool.h>`, `<stddef.h>`, and `<stdint.h>`. Relies on configure-provided `HAVE___BUILTIN_*_OVERFLOW` macros and compiler extensions like `typeof`, statement expressions, and `__builtin_choose_expr`.

## Risks And Review Notes
- Fallback definitions for missing compiler builtins do not actually detect overflow; they assign the wrapped result and return false.
- The fallback guard for `__builtin_sub_overflow` checks `!HAVE___BUILTIN_MUL_OVERFLOW`, which looks like a copy/paste error; it should likely be controlled by a subtraction-specific configure macro.
- Type-checking intentionally requires operands and destination pointed-to type to match, which is stricter than GCC builtins.
