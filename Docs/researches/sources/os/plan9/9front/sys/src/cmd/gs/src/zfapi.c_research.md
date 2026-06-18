# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfapi.c

Implements the Ghostscript Font API client that delegates font preparation and glyph rendering to external renderer plugins.

Key behavior:
- Defines path callbacks for converting renderer outlines into Ghostscript paths, including optional closepath repair.
- Provides readers/writers for Type 42 `sfnts` arrays and serializes TrueType data while omitting `glyf`, `loca`, and `cmap` tables for renderer use.
- Exposes font feature callbacks for Type 1, Type 2, CID, and Type 42 data: font matrices, blue values, stem snaps, subrs/global subrs, glyph strings, TrueType glyph data, and glyph-directory data.
- Selects FAPI plugins, opens renderers, prepares scaled fonts, refines FontBBox, installs Decoding/SubstNWP metadata, and registers cleanup notifiers.
- Rebuilds fonts by replacing BuildChar/BuildGlyph procedures with `.FAPIBuildChar`, `.FAPIBuildGlyph`, or `.FAPIBuildGlyph9`.
- Implements glyph rendering flow: resolve char code/name/CID, prepare font scale and oversampling, provide glyph data, reconcile metrics, set cache device, and finish with raster copy or outline fill/stroke.
- Implements `.FAPIavailable`, `.FAPIpassfont`, `.FAPIrebuildfont`, `.FAPIBuildChar`, `.FAPIBuildGlyph`, and `.FAPIBuildGlyph9`.

Dependencies:
- Integrates font internals, CID mapping, Type 1 encryption, Type 42 sfnts, text enumeration/cachedevice, plugins, device raster APIs, and path painting.

Research notes:
- This is high-risk integration glue. Correctness depends on plugin contracts, glyph data lifetime, VM allocation, metrics substitution, oversampling retry, and renderer cleanup.
