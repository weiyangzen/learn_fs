# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhintn.c

Purpose: implements Ghostscript's newer Type 1/Type 2 font hinter. It imports charstring outline operations into internal pole/hint arrays, aligns stems and blue-zone features to device/subpixel grids, interpolates unaligned points, and exports the adjusted outline into a `gx_path`.

Key responsibilities:
- Fixed-point transform support: `double_matrix`/`fraction_matrix` setup, inversion, precision reduction, glyph-to-outliner/device conversions.
- Font setup: `t1_hinter__set_mapping`, `t1_hinter__set_font_data`, and `t1_hinter__set_font42_data` configure CTM, pixel/subpixel scale, blue zones, stem snaps, ForceBold, autohint defaults, and disabled-hinting behavior.
- Outline capture: `sbw`, `rmoveto`, `rlineto`, `rcurveto`, `closepath`, flex handlers, and `setcurrentpoint` accumulate poles and contours unless hinting is disabled, in which case they directly emit transformed path segments.
- Hint capture: `hstem`, `vstem`, `hstem3`, `vstem3`, `hint_mask`, `drop_hints`, `dotsection`, and range bookkeeping store stem commands and activation ranges.
- End-of-glyph processing: `t1_hinter__endglyph` adds trailing moveto, computes spans, simplifies representation, computes hint ranges, aligns stems, adjusts opposite boundaries, processes dotsections, interpolates remaining poles, exports the path, and frees dynamic arrays.

Important data flow:
- Glyph-space coordinates are stored in `t1_pole.gx/gy`; aligned glyph-space coordinates are stored in `ax/ay`.
- Hints store original stem boundaries `g0/g1`, aligned boundaries `ag0/ag1`, range lists, side masks, and alignment strength.
- Dynamic arrays start with embedded fixed-size buffers from `gxhintn.h` and grow via `gs_alloc_bytes` when limits are exceeded.

Alignment behavior:
- Horizontal stems use Y coordinates; vertical stems use X coordinates.
- Blue zones can force top/bottom alignment and overshoot suppression.
- Standard stem widths are consulted when preserving stem width.
- Dotsections are shifted toward nearby vertical stem centers or half-pixel alignment when not already aligned by stem hints.
- Remaining points are interpolated between aligned poles, with extra handling around extrema.

Dependencies:
- Uses Ghostscript path, font, matrix, fixed-point, memory, error, and optional `vdtrace` debugging APIs.
- Public entry points are declared in `gxhintn.h`.

Research notes:
- This is graphics/font rendering code, not filesystem code, but it is part of the Plan 9 Ghostscript source tree included in subset A.
- Several comments identify compatibility workarounds and known limitations: diagonal stems are not hinted, some font-size/resolution calculations are known imperfect, and some glyph-validity assumptions are heuristic.
