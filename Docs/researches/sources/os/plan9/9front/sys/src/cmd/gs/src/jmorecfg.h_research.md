# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jmorecfg.h

Generated/copied Ghostscript wrapper for IJG `jmorecfg.h`. It is byte-identical to `jmorecf0.h` in this tree and has the same `gsjmorec_INCLUDED` include guard.

It includes `jmcorig.h`, then customizes the local JPEG build by disabling selected optional features and preserving only the decoder capabilities Ghostscript needs for PDF/PostScript input. The key retained behavior is progressive/multiscan decode support; the key Ghostscript-specific compatibility change is `D_MAX_BLOCKS_IN_MCU 64` for Adobe DCT streams.

Because it has the canonical name `jmorecfg.h`, public `jpeglib.h` includes this file directly. `jpeg.mak` produces it from `jmorecf0.h` when building with the local JPEG library.

Filesystem relevance: none directly. It is a generated/copied codec configuration header in userland Ghostscript.
