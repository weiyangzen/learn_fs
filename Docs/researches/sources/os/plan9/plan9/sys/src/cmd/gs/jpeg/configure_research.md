# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/configure

Autoconf 2.12-generated configure script for the IJG JPEG library subtree.

Key behavior:
- Parses standard configure options plus IJG additions: `--enable-shared`, `--enable-static`, and `--enable-maxmem[=N]`; also supports older `--with-maxmem`.
- Sets installation directory variables, program transform options, cache/site handling, source directory discovery, logging to `config.log`, and locale normalization.
- Locates an acceptable C compiler, detects cross-compilation, GNU C, C preprocessor invocation, and default CFLAGS.
- Probes C language/library features: function prototypes, stddef/stdlib/string headers, `size_t`, unsigned char/short, `void`, working `const`, inline spelling, incomplete type behavior, short external names, char signedness, signed right shift, and binary `fopen("b")` support.
- Locates `install-sh`/`install.sh`, selects a BSD-compatible install program, and finds `ranlib`.
- Optionally configures GNU libtool via `ltconfig`, setting object/library suffix variables and install/link commands.
- Chooses memory manager object: `jmemnobs.$(O)` by default, `jmemansi.$(O)` when maxmem and `tmpfile()` are available, or `jmemname.$(O)` with signal catcher/mktemp checks otherwise.
- Extracts `JPEG_LIB_VERSION` from `jpeglib.h`.
- Decides whether `ansi2knr` is needed based on prototype support and whether `-DBSD` is needed for it.
- Generates `config.status`, then creates `Makefile` from `makefile.cfg` and `jconfig.h` from `jconfig.cfg`.

Dependencies:
- Requires POSIX-ish `/bin/sh`, sed, grep/egrep, compiler/linker tools, source files such as `jcmaster.c`, templates `makefile.cfg` and `jconfig.cfg`, and helper scripts such as `install-sh`; optional libtool files are used when shared/static libtool builds are enabled.

Research notes:
- This is generated build infrastructure, not handwritten runtime code.
- Cross-compiling paths use assumptions for char signedness, right shift, and binary fopen behavior.
- The script creates and removes `conftest*`, `confdefs*`, `config.log`, `config.cache`, and `config.status` artifacts during normal execution.
