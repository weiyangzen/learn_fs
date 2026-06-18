# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zicc.c

LanguageLevel 3 ICCBased color-space operator implementation. It registers `.seticcspace`, which receives the ICCBased dictionary after surrounding PostScript code has selected or implied the alternate color space.

`zseticcspace` reads `/N`, validates `/DataSource` as a readable file stream, rejects unsuitable alternate spaces and nested ICCBased alternate spaces, then reads the optional `Range` array with defaults of `[0 1]` per component. It verifies every range has `min <= max`.

The operator builds a CIEICC color-space object, stores the ICC stream, stream file id, component count, and ranges, copies the current color space as the alternate space, increments its color-space reference count, loads the ICC profile with `gx_load_icc_profile`, prepares CIE caches with `cie_cache_joint`, and finishes installation through `cie_set_finish`. The file is the interpreter bridge between ICC profile streams and Ghostscript’s CIE/ICC color machinery.
