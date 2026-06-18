# File Research: sources/virtualization/nvme-cli/ccan/ccan/ilog/ilog.h

- Purpose: integer binary logarithm API and compile-time helpers.
- Key APIs: `ilog32`, `ilog32_nz`, `ilog64`, `ilog64_nz`, `STATIC_ILOG_32`, and `STATIC_ILOG_64`.
- Compiler optimization: maps to `__builtin_clz`, `__builtin_clzl`, or `__builtin_clzll` when available.
- Constant handling: uses nested macros `STATIC_ILOG0` through `STATIC_ILOG6` for compile-time values.
- Notable quirk: in the `builtin_ilog64_nz` block, the header redefines `ilog32(_v)` instead of `ilog64(_v)`, which is worth reviewing if editing this file.
