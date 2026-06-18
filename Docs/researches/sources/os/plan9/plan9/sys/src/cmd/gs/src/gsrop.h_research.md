# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrop.h

Declares RasterOp and transparency procedures.

Exports:
- `gs_setrasterop`
- `gs_currentrasterop`
- `gs_setsourcetransparent`
- `gs_currentsourcetransparent`
- `gs_settexturetransparent`
- `gs_currenttexturetransparent`
- `gs_current_logical_op`
- `gs_set_logical_op`

Integration:
- Includes `gsropt.h` for `gs_rop3_t` and `gs_logical_operation_t`.
- Implemented by `gsrop.c`.

Risk notes:
- Thin header; semantics depend on `gsrop.c` and graphics-state invariants.
