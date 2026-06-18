# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jasper.mak

Makefile fragment for integrating the Jasper JPEG 2000 library with Ghostscript. It supports either linking to a shared/external Jasper library or compiling selected Jasper 1.701.x source files into Ghostscript.

Defines source, object, and generated directories; object groups for base, JPC, and JP2 components; header dependencies; clean targets; Jasper-specific compile flags; excluded format support macros; generated `.dev` module rules; and explicit compile rules for each selected Jasper source.

The fragment intentionally disables unrelated Jasper image formats and builds only the pieces Ghostscript needs for JPEG 2000 support.
