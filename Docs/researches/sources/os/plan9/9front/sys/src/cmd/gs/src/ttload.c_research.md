# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttload.c

Loader implementation for the subset of TrueType tables needed by this Ghostscript TrueType instruction runtime.

Key points:
- Implements `Load_TrueType_MaxProfile`.
  - Seeks to `maxp`.
  - Reads version, glyph count, point/contour maxima, twilight/storage/function/instruction/stack/instruction-size maxima, component maxima.
  - Derives `face->numGlyphs`, `face->maxPoints`, `face->maxContours`, and `face->maxComponents`.
- Implements `Load_TrueType_CVT`.
  - Seeks to `cvt `.
  - Computes `face->cvtSize` from table length / 2.
  - Allocates `face->cvt`.
  - Reads signed short CVT values until the table ends or reader EOF.
- Implements `Load_TrueType_Programs`.
  - Loads optional `fpgm` font program into `face->fontProgram`.
  - Loads optional `prep` CVT program into `face->cvtProgram`.
  - Allocates program byte buffers from Ghostscript’s `ttfMemory`.
- Uses debug trace macros tied to the font’s `DebugPrint` callback.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `tttypes.h`, `ttcalc.h`, `ttobjs.h`, `ttload.h`, and `ttfinp.h`.
- Uses `ttfReader` callbacks for `Seek`, `Read`, and `Eof`.
- Uses table metadata fields from `ttfFont` such as `t_maxp`, `t_cvt_`, `t_fpgm`, and `t_prep`.
- Called from `Face_Create` in `ttobjs.c`.

Research relevance:
- Supplies the interpreter with maximum allocation limits, the unscaled CVT, and executable TrueType programs. It is intentionally narrower than a full font loader.
