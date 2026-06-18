# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcid.h

This header defines internal structures and procedures for CID-keyed fonts in Ghostscript. It includes CID system info, base font, and Type 42 font headers.

`gs_font_cid_data` is common to CIDFontType 0 and 2: `CIDSystemInfo`, `CIDCount`, and optional `GDBytes` for standard glyph data. GC descriptor macros build on `st_cid_system_info`.

CIDFontType 0 (`gs_font_cid0`) stores common CID data plus `CIDMapOffset`, an FDArray of partial Type 1 fonts, FDArray size, `FDBytes`, a `glyph_data` callback that can return glyph data and/or font number, and callback private data.

CIDFontType 1 (`gs_font_cid1`) is minimal, carrying base font common data plus `CIDSystemInfo`.

CIDFontType 2 (`gs_font_cid2`) subclasses Type 42. It stores common CID data, `MetricsCount`, a `CIDMap_proc`, and saved original Type 42 outline/metrics procedures so wrappers can account for CID-specific metrics behavior.

The header declares `gs_font_cid_system_info`, a simple CIDFontType 0 glyph enumerator, CIDSystemInfo compatibility checking, FDArray indexed-font lookup, and a predicate for whether a CID font has a Type 2 subfont.

Filesystem relevance: none. This is font representation code.
