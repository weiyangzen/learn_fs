# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrop.c

Implements public RasterOp and transparency accessors for the graphics state.

Main behavior:
- `gs_setrasterop` updates the raster-op bits of `pgs->log_op`.
- `gs_currentrasterop` extracts the current RasterOp.
- `gs_setsourcetransparent` and `gs_settexturetransparent` toggle source/texture transparency bits.
- `gs_currentsourcetransparent` and `gs_currenttexturetransparent` read those bits.
- `gs_set_logical_op` and `gs_current_logical_op` set/get the entire combined logical operation for internal save/restore.

All setters reject changes while in `cachedevice`, returning `undefined`.
