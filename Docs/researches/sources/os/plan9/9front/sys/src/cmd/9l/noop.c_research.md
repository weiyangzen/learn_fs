# File Research: sources/os/plan9/9front/sys/src/cmd/9l/noop.c

This file performs late instruction-stream cleanup and prologue/epilogue expansion before scheduling and spanning.

Key routines:
- `noops` marks leaf routines, detects branches/sync/floating operations, strips `ANOP`, computes frame and `BECOME` sizes, expands `TEXT` prologues, expands `RETURN`, handles `BECOME` pseudo-returns, and optionally schedules instruction blocks.
- `addnop` inserts a Power64 no-op encoded as `OR R0,R0`.

Important interactions:
- Runs after `follow` and before `span`.
- Uses symbol fields `frame`, `become`, and type `SLEAF`.
- Calls `sched` when instruction scheduling is enabled via `debug['Q']`.
- Inserts LR save/restore through `REGTMP`, `REGSP`, and special register `D_LR`.

Research notes:
- Leaf functions with no frame suppress stack adjustment and LR save/restore.
- Non-leaf prologues save LR through `REGTMP` and may use `MOVDU` for compact SP adjustment.
- `BECOME` support adjusts frame sizes across calls and rewrites returns into tail branches.
