# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iinit.h

Declares internal initialization stages exported by `iinit.c`.

Key points:
- Declares the required order:
  - `obj_init`
  - `zop_init`
  - `op_init`
- Declares `gs_have_level2`.
- Notes `gs_have_level2` checks compiled operators, not the runtime language level.

Dependencies and interactions:
- Used by `imain.c` during staged interpreter initialization.

Research relevance:
- Compact contract for interpreter object/operator initialization ordering.
