# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/fapiufst.c

Ghostscript Font API plug-in backed by Agfa UFST.

Key points:
- Implements an `FAPI_server` named `AgfaUFST`.
- Lazily initializes UFST with `CGIFinit`, `CGIFconfig`, and `CGIFenter`.
- Tracks server state in `fapi_ufst_server`, including UFST `IF_STATE`, current `FONTCONTEXT`, cached glyph/raster data, client memory callbacks, FCO font handles, transform state, and metric replacement state.
- Detects disk font type by reading leading bytes from the font file: FCO, PostScript Type 1, or TrueType.
- Builds UFST-compatible font data for embedded Type 1 and TrueType fonts, including PCL/PCLEO/PSEO headers and serialized subr/glyph data.
- Provides callback bridges `gs_PCLchId2ptr` and `gs_PCLglyphID2Ptr` so UFST can request glyph data from Ghostscript.
- Chooses decoding IDs from an `xlatmap`, including TrueType cmap platform/specific IDs.
- Handles FCO file open/reference counting through `CGIFfco_Open` and `CGIFfco_Close`.
- Provides FAPI callbacks for scaled fonts, decoding IDs, bounding boxes, proportional feature detection, glyph-name support, metric replacement, width metrics, raster/outline metrics, raster/outline retrieval, char-data release, and typeface release.
- Cleans stale UFST char data defensively because Ghostscript cannot always signal interrupted raster/outline sequences.

Dependencies and interactions:
- Uses UFST headers and APIs plus Ghostscript FAPI/plugin headers.
- Stores `ufst_common_font_data` in `FAPI_font.server_font_data`.
- Uses Ghostscript client memory alloc/free functions for font data, glyph caches, and FCO tracking.

OS/filesystem relevance:
- Opens disk fonts with `fopen(..., "rb")`; the comment notes `gp_fopen` is not better because UFST itself uses `fopen`.
- Disk font paths, FCO handle tracking, and font type probing are the main file-facing behavior.
