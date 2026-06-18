# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/libpng.mak

## Purpose
Ghostscript partial makefile for building or sharing libpng support used by PNG output drivers.

## Main Structure
- Maps historical Ghostscript variables `PSRCDIR`/`PVERSION` to `PNGSRCDIR`/`PNGVERSION`.
- Defines PNG source/generated/object directory aliases and `PNGCC`.
- Provides `png.clean`, `png.config-clean`, and object rules for selected libpng writer-side modules.
- Defines `libpng.dev` as a copy of either `libpng_0.dev` or `libpng_1.dev` depending on `SHARE_LIBPNG`.

## Important Build Products
- Compiled objects: `png`, `pngwio`, `pngmem`, `pngerror`, `pngset`, `pngtrans`, `pngwrite`, `pngwtran`, `pngwutil`.
- `libpng_1.dev`: shared-lib wrapper that links `LIBPNG_NAME` and includes zlib encode support.
- `libpng_0.dev`: static module grouping PNG objects and including zlib plus version-specific `lpg$(PNGVERSION).dev`.
- `lpg$(PNGVERSION).dev`: version-specific module for `pngwio` plus zlib `crc32`.

## Integration Notes
- Must be included after zlib support because `zlibe.dev` and `crc32.dev` are required.
- Used by platform makefiles that set `SHARE_LIBPNG`, `LIBPNG_NAME`, and libpng source version variables.

## Risks and Edge Cases
- Comment explicitly states clean rules are broad and “wrong” because they delete object files non-selectively.
- Only a subset of libpng modules is built here, aimed at Ghostscript writer/output use rather than a complete standalone libpng build.
