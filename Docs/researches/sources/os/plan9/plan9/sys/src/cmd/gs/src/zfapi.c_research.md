# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfapi.c

Implements the Ghostscript client side of the Font API plugin interface.

Major responsibilities:
- Adapt Ghostscript font dictionaries and font structs to `FAPI_font`.
- Provide callbacks for Type 1, CID, and Type 42 glyph/subroutine data.
- Serialize TrueType `sfnts` without `glyf`, `loca`, and `cmap` tables when needed.
- Install FAPI build procedures into fonts.
- Render characters through external FAPI renderer plugins while preserving Ghostscript cache/device semantics.

Key data bridges:
- `sfnts_reader` and `sfnts_writer` iterate over fragmented `sfnts` arrays and construct stripped SFNT data.
- `FAPI_FF_get_word()`, `FAPI_FF_get_long()`, and `FAPI_FF_get_float()` expose font feature fields.
- `FAPI_FF_get_subr()` and `FAPI_FF_get_glyph()` expose Type 1 subrs/global subrs and glyph data, including decryption when required.
- `get_GlyphDirectory_data_ptr()` handles CID GlyphDirectory string/array/dictionary access.

Font preparation:
- `FAPI_find_plugin()` locates a named FAPI renderer and opens it.
- `FAPI_prepare_font()` calls renderer `get_scaled_font()` for top-level and descendant fonts, retrieves font bbox, optionally gets decoding IDs, and releases renderer font data on failure.
- `FAPI_refine_font()` updates `FontBBox` and writes decoding/substitution names into font dictionaries.
- `zFAPIpassfont()` tries available FAPI plugins and inserts `/FAPI` into the font dictionary on success.
- `zFAPIrebuildfont()` replaces BuildChar/BuildGlyph refs with `.FAPIBuildChar`, `.FAPIBuildGlyph`, or `.FAPIBuildGlyph9`.

Rendering path:
- `FAPI_do_char()` computes font scale from CTM, device resolution, oversampling, CID/vertical metrics, encoding/decoding, glyph IDs, and metrics replacement state.
- It queries renderer metrics/raster/outline, sets Ghostscript cache device through `zchar_set_cache()`, and schedules `fapi_finish_render()`.
- `fapi_finish_render_aux()` either emits outlines into charpath/fill/stroke paths or copies/fill-masks renderer raster data to the target/current device.

CIDFontType 0 integration includes `.FAPIBuildGlyph9`, which maps CID through `ztype9mapcid()` and delegates rendering to the selected descendant font.

Registered operators: `.FAPIavailable`, `.FAPIpassfont`, `.FAPIrebuildfont`, `.FAPIBuildChar`, `.FAPIBuildGlyph`, and `.FAPIBuildGlyph9`.

Notable risk areas: many assumptions are documented as comments, including renderer cache behavior, glyph data lifetime between metrics and raster calls, SFNT/TTC limitations, and approximations in metrics replacement/oversampling fallback.
