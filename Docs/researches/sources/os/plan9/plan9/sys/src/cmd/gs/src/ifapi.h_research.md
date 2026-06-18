# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifapi.h

Defines Ghostscript’s Font API plugin interface.

Key points:
- Includes `iplugin.h`.
- Defines `FracInt`, `FAPI_retcode`, `fapi_font_feature`, `FAPI_metrics_type`, and FAPI descriptor structures.
- `FAPI_font` carries server font state, client font state, font source path/subfont flags, character data, and callbacks for font features, subrs, glyphs, and serialized TrueType data.
- `FAPI_path` abstracts outline callbacks: `moveto`, `lineto`, `curveto`, `closepath`.
- `FAPI_font_scale`, `FAPI_metrics`, and `FAPI_raster` describe scaling, metrics, and 1-bit raster output.
- `FAPI_server` extends `i_plugin_instance` and exposes callbacks for opening a backend, acquiring scaled fonts, decoding IDs, metrics, raster/outline retrieval, and release.
- Comments clarify that Ghostscript cannot tell the server when scaled fonts are no longer used; the server or bridge must cache and evict internally.

Research relevance:
- Important interpreter/plugin boundary for delegating font scaling, metrics, rasterization, and outline extraction to external font backends.
