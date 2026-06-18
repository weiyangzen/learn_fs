# File Research: sources/virtualization/nvme-cli/ccan/ccan/check_type/check_type.h

- Purpose: macro-level type checking for C APIs.
- Key APIs: `check_type(expr, type)` and `check_types_match(expr1, expr2)`.
- Fast path: uses `typeof` pointer comparison to produce warnings/errors without evaluating expressions.
- Fallback: checks only `sizeof` equality when `typeof` is unavailable.
