# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zrop.c

RasterOp and transparency flag operators. It registers current/set forms for raster operation, source transparency, and texture transparency.

`setrasterop` reads an integer in `0..0xff` and calls `gs_setrasterop`. `currentrasterop` pushes the current logical operation. The source/texture transparent setters read booleans and update graphics-state RasterOp transparency flags; current operators push the current booleans.

This is a small PostScript wrapper over `gsrop.h` state. It is relevant to painting/compositing behavior but contains no raster implementation itself.
