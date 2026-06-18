# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-gcc.mak

Purpose: Top-level makefile for building Ghostscript on DesqView/X with GCC and X11.

Key build configuration:
- Directory defaults: `BINDIR=bin`, `GLSRCDIR=src`, generated/object dirs under `obj`, `PSLIBDIR=lib`.
- Install defaults: `prefix=c:/bin`, `gsdatadir=c:/gs`, `gsfontdir=c:/gsfonts`.
- Runtime library path: `GS_LIB_DEFAULT="$(gsdatadir)/lib;$(gsdatadir)/Resource;$(gsfontdir)"`.
- Compiler/linker: `CC=gcc`, `CFLAGS=-O $(XCFLAGS)`, `EXTRALIBS=-lsys -lc`, `STDLIBS=-lm`.
- X11 settings: default `XLIBS=Xt Xext X11`.
- Feature devices include PostScript Level 3, PDF, DPS, TrueType, EPSF, pipe, and FAPI.
- Default output device is `x11.dev`, with many printer/image/pdfwrite devices enabled across `DEVICE_DEVS*`.

Included makefiles:
- `dvx-head.mak`, `gs.mak`, `lib.mak`, `int.mak`, `cfonts.mak`, JPEG/zlib/libpng/jbig2/icclib/ijs makefiles, `devs.mak`, `contrib.mak`, `dvx-tail.mak`, `unix-end.mak`, `unixinst.mak`.

Filesystem relevance: Build/install paths and runtime search paths only. No OS filesystem implementation.
