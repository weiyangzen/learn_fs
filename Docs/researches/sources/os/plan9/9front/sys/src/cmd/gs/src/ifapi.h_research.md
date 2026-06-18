# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifapi.h

Defines Ghostscript’s Font API plugin interface.

Key points:
- Includes `iplugin.h`.
- Defines `FracInt` and `FAPI_retcode`.
- Defines `fapi_font_feature` enum for PostScript/Type1/TrueType font properties such as `FontMatrix`, `UniqueID`, blue values, stem snaps, `Subrs`, and TrueType size.
- Defines metric replacement modes in `FAPI_metrics_type`.
- `FAPI_char_ref` identifies a character by code, glyph index, or name and can carry replacement metrics.
- `FAPI_font` carries server-owned font data, client context, font source path, Type1/CID flags, char data, and callback functions for retrieving font features, subrs, glyphs, and serialized TrueType data.
- `FAPI_path` abstracts outline callbacks: `moveto`, `lineto`, `curveto`, `closepath`.
- `FAPI_font_scale`, `FAPI_metrics`, and `FAPI_raster` describe scaling, metrics, and 1-bit raster output.
- `FAPI_server` extends `i_plugin_instance` and exposes plugin/server callbacks for opening, scaled-font acquisition, decoding IDs, metrics, raster/outline retrieval, and data/typeface release.
- Comments clarify that Ghostscript cannot tell the server when scaled fonts are no longer used; the server must cache and evict internally.

Dependencies and interactions:
- Used by FAPI bridge/plugin code such as `zfapi.c`.
- Coordinates font data retrieval between the interpreter and external font backends.

Research relevance:
- Important extension boundary: the interpreter delegates font scaling/raster/outline operations through this ABI-like interface.
