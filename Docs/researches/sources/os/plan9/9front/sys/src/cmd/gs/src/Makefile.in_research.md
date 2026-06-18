# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/Makefile.in

This is the autoconf `Makefile` template for building Ghostscript on Unix-like systems. It defines install paths, source and object directories, compiler/linker variables, feature/device lists, and includes the rest of the Ghostscript build fragments.

Key responsibilities:
- Defines build directories such as `BINDIR`, `GLSRCDIR`, `GLGENDIR`, `GLOBJDIR`, `PSSRCDIR`, `PSLIBDIR`, `PSGENDIR`, and `PSOBJDIR`.
- Substitutes autoconf outputs for install prefixes, compiler settings, X11 paths, optional libraries, and selected devices.
- Configures default runtime search paths with `GS_LIB_DEFAULT`, including Ghostscript data, resources, and fonts.
- Controls security-relevant search behavior through `SEARCH_HERE_FIRST=1`, with comments acknowledging known confusion and security issues.
- Selects bundled or shared support libraries: JPEG, PNG, zlib, JBIG2, JasPer, ICC, and IJS.
- Defines language features and output device groups, including PNG devices via `@PNGDEVS@`.
- Includes the build fragments in dependency order, notably `zlib.mak` before `libpng.mak`.

Important build relationships:
- `configure.ac` fills substitutions such as `@LIBPNGDIR@`, `@SHARE_LIBPNG@`, `@ZLIBDIR@`, `@X11DEVS@`, and `@PNGDEVS@`.
- `cfonts.mak` is included for compiled fonts.
- `contrib.mak` is included after core device makefiles to expose user-contributed devices.
- `distclean` removes generated configuration/build files, while `maintainer-clean` also removes autotools inputs generated through the source setup flow.

Notable implementation details and risks:
- The makefile is for Unix-style Ghostscript builds, not Plan 9 mkfiles.
- It defaults to `SYNC=nosync` and `STDLIBS=-lm`, with comments explaining pthread needs if POSIX sync is enabled.
- PNG output devices depend on libpng and zlib discovery from configure.
- The default `SEARCH_HERE_FIRST=1` is explicitly called out as risky but preserved for user expectations.
- No filesystem implementation logic is present; this is build orchestration.

Research classification: Ghostscript Unix build template, relevant to dependency and device composition for the vendored Ghostscript tree.
