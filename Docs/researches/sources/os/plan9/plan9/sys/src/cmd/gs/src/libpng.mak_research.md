# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/libpng.mak

`libpng.mak` is a partial Ghostscript makefile for PNG output support. It maps historical Ghostscript variable names `PSRCDIR` and `PVERSION` onto `PNGSRCDIR` and `PNGVERSION`, then derives source, generated, and object directories.

The file compiles libpng writer-side modules such as `png.c`, `pngmem.c`, `pngerror.c`, `pngset.c`, `pngtrans.c`, `pngwrite.c`, `pngwtran.c`, `pngwutil.c`, and `pngwio.c`. `PNGCC` uses Ghostscript-provided include and flag macros.

It supports either shared or bundled libpng. `libpng.dev` is copied from `libpng_$(SHARE_LIBPNG).dev`; shared mode emits a `-lib $(LIBPNG_NAME)` module and includes zlib, while bundled mode collects local PNG objects, includes zlib, and adds a version-specific `lpg$(PNGVERSION).dev` helper for `pngwio` plus `crc32`.

The file is tightly integrated with `zlib.mak`, since PNG modules require zlib encode support. A maintenance note says the clean target is wrong because it deletes object/generated files too broadly rather than selectively.
