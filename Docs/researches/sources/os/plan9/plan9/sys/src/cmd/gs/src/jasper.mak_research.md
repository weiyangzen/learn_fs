# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jasper.mak

Purpose: Ghostscript partial makefile for integrating the JasPer JPEG 2000 support library.

Build model:
- Supports either linking an external `jasper` library (`SHARE_JASPER=1`) or compiling selected JasPer source files into Ghostscript (`SHARE_JASPER=0`).
- Defines source/object/generated directories, object lists for base, JPC, and JP2 components, and header dependency lists.
- Generates `libjasper.dev` by copying the selected shared/compiled `.dev` module file.
- Compiled mode builds explicit object rules for selected JasPer 1.701.x source files.

Configuration details:
- `JAS_EXCF_` disables unrelated JasPer formats such as BMP, JPG, MIF, PGX, PNM, RAS, and PNG, leaving the JPEG 2000 paths Ghostscript needs.
- Clean targets remove generated `.dev` files and object files, with comments noting object/gen deletion should be more selective.

Research notes: This is build integration for an embedded third-party image codec, not runtime code.
