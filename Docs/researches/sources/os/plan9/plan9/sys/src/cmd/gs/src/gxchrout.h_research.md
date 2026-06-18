# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchrout.h

Header for shared outline character rendering helpers. It forward-declares `gs_imager_state` and declares `gs_char_flatness(const gs_imager_state *, floatp)`. The comments document the key contract: the returned flatness may be smaller than the imager state flatness, and the caller supplies the font’s default scaling, typically `0.001` for Type 1 fonts or `1.0` for TrueType fonts.
