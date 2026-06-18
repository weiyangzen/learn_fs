# File Research: sources/virtualization/nvme-cli/ccan/ccan/array_size/array_size.h

- Purpose: CCAN macro for compile-time-safe visible array length.
- Key API: `ARRAY_SIZE(arr)`.
- Safety: with `typeof` and `__builtin_types_compatible_p`, rejects pointer arguments by comparing array type to `&arr[0]` pointer type.
- Dependency: uses `BUILD_ASSERT_OR_ZERO`.
