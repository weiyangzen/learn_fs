# File Research: sources/virtualization/nvme-cli/ccan/ccan/ilog/ilog.c

- Purpose: callable implementations of integer binary logarithm functions.
- Key APIs implemented: `ilog32`, `ilog32_nz`, `ilog64`, and `ilog64_nz`.
- Algorithms: uses de Bruijn sequence fallback by default, with branch-based fallback when `ILOG_NODEBRUIJN` is defined.
- Note: compiled even when header macros use compiler builtins, so address-taking still works.
