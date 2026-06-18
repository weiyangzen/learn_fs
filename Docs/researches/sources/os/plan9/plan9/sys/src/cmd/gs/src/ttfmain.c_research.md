# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmain.c

Purpose: Ghostscript adapter around FreeType-derived TrueType face setup, hinting context, glyph loading, compound glyph expansion, and outline export.

Key contents:
- Defines fixed and floating transform helpers, `FixMatrix`, and `ttfSubGlyphUsage`.
- Implements `TT_Set_Instance_CharSizes` to set instance metrics and reset the TrueType instance.
- Implements interpreter reference management through `ttfInterpreter__obtain` and `ttfInterpreter__release`.
- Implements `ttfFont__init`, `ttfFont__finit`, and `ttfFont__Open`.
- `ttfFont__Open` handles TTC collections, sfnt version checks, table directory parsing, key table offsets, units-per-em, glyph counts, component limits, metrics counts, interpreter usage allocation, face/context/instance creation, CVT scaling, preprogram execution, and size setup.
- Implements glyph lifecycle helpers `ttfFont__StartGlyph` and `ttfFont__StopGlyph`.
- Implements FreeType-style glyph-zone helpers: `mount_zone`, `Init_Glyph_Component`, `cur_to_org`, and `org_to_cur`.
- Implements `ttfOutliner__init`, private glyph transform/move helpers, recursive `ttfOutliner__BuildGlyphOutlineAux`, wrapper `ttfOutliner__BuildGlyphOutline`, `ttfOutliner__DrawGlyphOutline`, and public `ttfOutliner__Outline`.
- Handles simple glyphs, compound glyphs, horizontal/vertical metrics, phantom points, glyph instruction execution through `Context_Run`, and conversion of quadratic TrueType curves into exported cubic curves or lines.
- Includes explicit handling for patented instruction failures (`fPatented`) and malformed font data.

Dependencies: `ttmisc.h`, `ttfoutl.h`, `ttfmemd.h`, `ttfinp.h`, `ttfsfnt.h`, `ttobjs.h`, `ttinterp.h`, `ttcalc.h`.

Integration notes: core external API is declared in `ttfoutl.h`; consumers provide `ttfReader` for data and `ttfExport` for outline emission.

Risks: recursive compound glyph processing is capped through `MAX_SUBGLYPH_NESTING` and usage array sizing. Reader callbacks must manage glyph buffer lifetime around `LoadGlyph`/`ReleaseGlyph`. Error handling often maps low-level TrueType errors into broad `FontError` categories.
