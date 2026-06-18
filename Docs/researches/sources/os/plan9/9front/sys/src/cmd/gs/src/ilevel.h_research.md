# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ilevel.h

Defines interpreter language-level convenience macros.

Key points:
- `LANGUAGE_LEVEL` maps to `i_ctx_p->language_level`.
- `LL2_ENABLED` checks `LANGUAGE_LEVEL >= 2`.
- `LL3_ENABLED` checks `LANGUAGE_LEVEL >= 3`.
- `level2_enabled` aliases `LL2_ENABLED` for backward compatibility.

Dependencies and interactions:
- Used throughout interpreter operators to gate Level 2/3 behavior.

Research relevance:
- Simple but widespread runtime language-level control contract.
