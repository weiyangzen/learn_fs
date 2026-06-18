# File Research: sources/virtualization/nvme-cli/ccan/ccan/compiler/compiler.h

- Purpose: portability layer for compiler attributes and builtins.
- Defines: `COLD`, `NORETURN`, `PRINTF_FMT`, `CONST_FUNCTION`, `PURE_FUNCTION`, `UNNEEDED`, `NEEDED`, `UNUSED`, `WARN_UNUSED_RESULT`, `WARN_DEPRECATED`, `NO_NULL_ARGS`, `NON_NULL_ARGS`, `RETURNS_NONNULL`, `LAST_ARG_NULL`, and `cpu_supports`.
- Feature gates: all macros depend on `HAVE_ATTRIBUTE_*`, `HAVE_BUILTIN_*`, and related config symbols.
- Research value: centralizes optional compiler diagnostics/optimization annotations used by other CCAN modules.
