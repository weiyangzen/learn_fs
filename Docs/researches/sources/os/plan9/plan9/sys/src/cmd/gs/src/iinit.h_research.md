# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iinit.h

Declares internal initialization stages exported by `iinit.c`.

Key points:
- Declares required initialization order: `obj_init`, `zop_init`, then `op_init`.
- Declares `gs_have_level2`.
- Notes `gs_have_level2` checks compiled operators, not runtime language level.

Research relevance:
- Compact contract for interpreter object/operator initialization ordering.
