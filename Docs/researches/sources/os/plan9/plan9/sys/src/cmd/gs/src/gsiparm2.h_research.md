# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm2.h

Defines ImageType 2 parameters from the Adobe PostScript Version 3010 Supplement.

`gs_image2_t` contains:
- Common image fields.
- `gs_state *DataSource`
- `XOrigin`, `YOrigin`
- `Width`, `Height`
- optional `gx_path *UnpaintedPath`
- `PixelCopy`

Provides `private_st_gs_image2` descriptor macro and declares `gs_image2_t_init`.

Defaults documented:
- `UnpaintedPath = 0`
- `PixelCopy = false`
