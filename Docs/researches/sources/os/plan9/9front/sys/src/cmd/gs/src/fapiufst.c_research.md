# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/fapiufst.c

## Scope

Ghostscript FAPI plugin for Agfa UFST font rendering.

## Key Behavior

- Initializes UFST through `CGIFinit`, `CGIFconfig`, and `CGIFenter`.
- Builds UFST font data for disk fonts, FCO fonts, embedded Type 1 fonts, and embedded TrueType fonts.
- Implements glyph callback paths for PCLEO/PCL Type 1 and TrueType glyph retrieval from Ghostscript FAPI.
- Chooses decoding IDs from translation maps for PostScript and TrueType fonts.
- Sets UFST `FONTCONTEXT` transforms, resolution, subpixel settings, symbol set, cmap platform/specific IDs, and vertical-writing flags.
- Provides FAPI operations for scaled-font preparation, bbox retrieval, proportional-font detection, name lookup capability, metrics replacement capability, width lookup, raster generation, outline generation, and resource release.

## Dependencies

Uses Ghostscript FAPI/plugin APIs plus UFST headers and functions such as `CGIFfont`, `CGIFchar_with_design_bbox`, `CGIFwidth`, `CGIFtt_query`, `CGIFtt_cmap_query`, `CGIFfco_Open`, and `gx_set_UFST_Callbacks`.

## Risks And Invariants

- The plugin assumes only one active UFST font context at a time because UFST caches `FONTCONTEXT` internally.
- Character raster/outline data is retained across paired calls and defensively released at later entry points to avoid leaks after Ghostscript-side errors.
- Many generated PCLEO header fields are marked approximate or “wrong” but apparently unused by UFST.
- Metrics replacement is limited to non-disk TrueType with skipped metrics and exact replacement semantics.
