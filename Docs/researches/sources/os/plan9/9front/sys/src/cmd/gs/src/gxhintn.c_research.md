# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhintn.c

## Role

`gxhintn.c` implements Ghostscript's "new algorithm" Type 1 hinter. It collects Type 1/Type 2 glyph outlines, stem hints, hint masks, flex points, alignment zones, and stem snap data in an internal `t1_hinter` object, grid-fits the outline in device-oriented space, then exports the adjusted outline to a `gx_path`.

This is font rasterization and outline processing infrastructure, not filesystem code.

## Main Responsibilities

- Sets up fixed/fraction matrix transforms between glyph space, internal outliner space, and device space.
- Initializes and tears down dynamic arrays for poles, hints, zones, contours, hint ranges, and stem snap widths.
- Imports charstring operations through `t1_hinter__sbw`, `rmoveto`, `rlineto`, `rcurveto`, `closepath`, `setcurrentpoint`, and flex handlers.
- Records Type 1/Type 2 hint operations through hstem/vstem/hstem3/vstem3, dotsection, hint masks, and hint dropping.
- Converts BlueValues/OtherBlues/FamilyBlues and stem snap data from font dictionaries into internal zones and standard widths.
- Computes hint ranges, detects stem-applicable outline poles, aligns stem boundaries and alignment zones, adjusts opposite stem coordinates, processes dotsections, interpolates unaligned points, and exports a final path.

## Important Algorithms

- `mul_shift`, `mul_shift_round`, `fraction_matrix__set`, and `fraction_matrix__invert_to` keep transformation arithmetic in bounded integer/fixed precision, with 64-bit multiply when available and a 32-bit fallback.
- `t1_hinter__adjust_matrix_precision` drops matrix precision dynamically when imported coordinates would exceed the 24-bit internal coordinate budget.
- `t1_hinter__compute_aligned_coord` combines stem alignment with BlueScale/BlueShift/BlueFuzz overshoot logic and optional stem-middle alignment.
- `t1_hinter__align_stem_width` and `t1_hinter__align_stem_to_grid` try to preserve stem width while snapping boundaries to pixels/subpixels and optionally using standard stem widths.
- `t1_hinter__interpolate_other_poles` propagates fitted coordinates around contours, splitting interpolation ranges at extrema and using fixed-point ratio approximation to avoid broad integer division/multiply overflow.
- `t1_hinter__endglyph` is the orchestration point: add trailing moveto, simplify representation, compute ranges, align stem commands, align poles, dotsection process, interpolate, paint debug traces, export, and free arrays.

## Dependencies And Integration

- Uses Ghostscript path, font, matrix, fixed-point, Type 1 data, and memory APIs from headers such as `gxpath.h`, `gxfont1.h`, `gxtype1.h`, `gxhintn.h`, `gzpath.h`, and `gserrors.h`.
- Emits device-space geometry through `gx_path_add_point`, `gx_path_add_line`, `gx_path_add_curve`, and `gx_path_close_subpath`.
- Uses `vdtrace` hooks for optional debug visualization.
- Depends on compile-time switches declared in `gxhintn.h`, including `FINE_STEM_COMPLEXES`, `ALIGN_BY_STEM_MIDDLE`, and compatibility/bug-fix switches.

## Notable Edge Cases

- If hinting is disabled or there is no output memory, path operations are emitted directly without delayed grid fitting.
- Degenerate transforms, very small/large CTMs, and import coordinates beyond the precision budget disable or reduce hinting precision.
- Type 1 primary hints are expanded to whole-glyph ranges; secondary hints cover replacement ranges; Type 2 hint masks keep explicit active ranges.
- Flex rendering may become either two curves or one line depending on flex height in device-oriented space.
- Dotsection adjustment is skipped if both X and Y extremes were already aligned by stems.

## Notable Risks

- The file is large, stateful, and macro/flag sensitive; correctness depends on many cross-field invariants in `t1_hinter`.
- Several comments mark unfinished areas: diagonal stems are not hinted, Adobe compatibility is not fully verified, anomalous negative contours are not repaired, and some font metrics for overshoot compatibility are known unreliable.
- There are suspicious implementation details worth auditing before modifying: `fraction_matrix__set` computes `ayx`/`ayy` from `pmat->xx`/`pmat->xy` rather than `pmat->yx`/`pmat->yy`; `t1_hinter__is_conjugated` computes `sp` with the same formula as `vp`; and `t1_hinter__process_dotsections` sets `end_pole` from `contour[contour_index] - 2`, which appears inconsistent with other contour-end calculations.
- `t1_hinter__endglyph` returns `0` after the cleanup label even if an earlier operation put a negative `code` in scope, so some errors before export cleanup may be masked.
