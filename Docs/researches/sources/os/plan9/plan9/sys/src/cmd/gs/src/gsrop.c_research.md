# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrop.c

Implements RasterOp and transparency state accessors for Ghostscript graphics state.

Key functions:
- `gs_setrasterop`: updates RasterOp bits in `pgs->log_op`, rejected inside cachedevice.
- `gs_currentrasterop`: extracts current ROP3 value.
- `gs_setsourcetransparent` / `gs_currentsourcetransparent`.
- `gs_settexturetransparent` / `gs_currenttexturetransparent`.
- `gs_set_logical_op` / `gs_current_logical_op`: internal save/restore of combined logical operation.

Integration:
- Uses `gzstate.h` graphics-state internals and `gsropt.h` bit definitions via `gsrop.h`.
- `gspaint.c` temporarily resets logical op for full-page fill.

Risk notes:
- Mutating RasterOp/transparency is disallowed during cachedevice, returning `undefined`.
- `gs_set_logical_op` is unrestricted internal API and can overwrite all logical-op bits.
