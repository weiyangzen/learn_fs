# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icolor.h

Declares transfer-function and color remapping cache helpers.

Key points:
- Exports required operand and execution stack slot counts for `zcolor_remap_one`.
- Declares `zcolor_remap_one`, which schedules sampling/reloading of a transfer map or recognizes special procedures.
- Declares finish routines for `[0..1]` and `[-1..1]` cache reloads.
- Declares helpers to recompute effective transfer functions and invalidate current color after remapping.

Research notes:
- This is interpreter glue for procedure-driven color cache construction.
- The scheduling contract always returns through continuation mechanics when remapping is handled.
