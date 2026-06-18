# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icclib.mak

Partial makefile for building Graeme W. Gill’s icclib inside Ghostscript.

Key points:
- Requires build variables for Ghostscript source, icclib source, generated intermediate files, and object directory.
- Notes the tested icclib version is 2.0 and defines `ICCPROFVER=9809`.
- Builds path variables for source, generated, and object outputs.
- Defines ICC include and compiler flags through Ghostscript make variables.
- Provides clean targets for generated `.dev` files and ICC object files.
- Builds `icclib.dev` from `icc.$(OBJ)` using `SETMOD`.
- Defines ICC header dependencies and compile rule for `icc.c`.

Research notes:
- This is build integration for a third-party ICC profile library.
- Comments admit the clean rule is broad and should delete generated/object files more selectively.
