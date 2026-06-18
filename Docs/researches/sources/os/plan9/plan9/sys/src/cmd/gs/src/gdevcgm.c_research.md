# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgm.c

Ghostscript CGM device wrapper that maps Ghostscript drawing operations into the local CGM-writing library.

Key responsibilities:
- Defines `cgmmono`, `cgm8`, and `cgm24` devices.
- Manages output file name, `FILE *`, CGM writer state, and picture-open state.
- Opens CGM files, initializes the CGM metafile, and declares metafile capabilities.
- Starts pictures lazily on first non-white drawing operation.
- Implements fill rectangle, monochrome bitmap copy, and color bitmap copy through CGM `RECTANGLE` and `CELL_ARRAY` elements.
- Provides `OutputFile` get/put support, including safety checks under `LockSafetyParams`.

Important behavior:
- `cgm_open` writes `BEGIN_METAFILE` and metafile attributes such as version, VDC type, integer/index/color precision, maximum color index, and element list.
- `cgm_begin_picture` sets abstract scaling, direct vs indexed color selection, VDC extent, edge width, optional color table, and begins the picture body.
- Indexed devices emit a CGM color table by asking the Ghostscript device to decode every color index.
- `cgm_output_page` closes the current picture if one is active.
- `cgm_close` closes any open picture, writes `END_METAFILE`, terminates the CGM state, and closes the output file.

Dependencies:
- Uses `gdevcgml.h` for CGM API calls and `gdevpccm.h` for 8-bit PC color mapping.
- Relies on Ghostscript device procs, file APIs, parameter lists, memory manager, and `fit_fill`/`fit_copy`.

Notable risks:
- If `cgm_initialize` fails after opening the file, the already-open file is not closed before returning VMerror.
- `cgm_copy_mono` slow path creates `fill_color` for each pixel but never calls `cgm_FILL_COLOR`, and it uses `cgm_set_rect(points, x, y, 1, 1)` instead of offsetting by `ix/iy`; transparent/nontrivial mono copies can therefore emit wrong rectangles/colors.
- The implementation intentionally lacks efficient tile/pattern support.
- `OutputFile` put handling may open the new file before the device open lifecycle expects the metafile header to be written.
