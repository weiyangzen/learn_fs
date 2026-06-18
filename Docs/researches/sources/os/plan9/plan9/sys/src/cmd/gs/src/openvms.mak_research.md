# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/openvms.mak

Legacy Ghostscript makefile for OpenVMS VAX and Alpha builds.

It defines OpenVMS-specific build directories, runtime library paths, compiler/linker command syntax, DEC C flags, X11 include handling, bundled third-party library locations, device lists, language features, file I/O choices, and generated header rules. It includes Ghostscript core make fragments such as `gs.mak`, `lib.mak`, `int.mak`, JPEG, zlib, libpng, JBIG2, ICC, device, and contrib makefiles.

Important behavior:

- Sets default runtime paths such as `GS_DOCDIR`, `GS_LIB_DEFAULT`, and `GS_INIT`.
- Configures OpenVMS compiler/linker commands including `/DECC`, `/PREFIX=ALL`, shortened names, include syntax, `.obj`/`.exe` suffixes, and DCL command helpers.
- Selects many display, printer, image, TIFF, PNG, JPEG, and PDF/PS output devices.
- Builds helper programs such as `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.
- Generates OpenVMS command and option files, including DECwindows shared library references.
- Generates `gconfig_.h` and `gconfigv.h` through `echogs`.

This file is build infrastructure for the bundled Ghostscript command tree. It has no filesystem implementation logic beyond build-time directory creation and generated-file rules.
