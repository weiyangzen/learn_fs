# File Research: sources/virtualization/nvme-cli/ccan/ccan/typesafe_cb/typesafe_cb.h

- Purpose: compile-time-assisted callback casting macros.
- Key APIs: `typesafe_cb_cast`, `typesafe_cb_cast3`, `typesafe_cb`, `typesafe_cb_preargs`, and `typesafe_cb_postargs`.
- Mechanism: when supported, uses `typeof`, `__builtin_choose_expr`, and `__builtin_types_compatible_p` to cast only matching callback types.
- Fallback: unconditional casts when compiler support is unavailable.
