# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/makefile.cfg

Purpose: autoconf-substituted makefile template for building and installing the IJG JPEG library and sample command-line programs.

Key contents:
- Configurable variables for source directory, install prefix, compiler, flags, libraries, libtool, object/archive suffixes, JPEG library version, memory manager backend, shell tools, installer, archiver, and ranlib.
- Source lists for library files, system-dependent memory manager backends, sample apps, headers, docs, makefiles, configuration files, configure support files, other support files, and tests.
- Object lists for common, compression, decompression, full library, and app-specific objects.
- Targets: `all`, `ansi2knr`, `libjpeg.a`, `libjpeg.la`, `cjpeg`, `djpeg`, `jpegtran`, `rdjpgcom`, `wrjpgcom`, `install`, `install-lib`, `install-headers`, `clean`, `distclean`, `test`, `check`, and `jconfig.h` mistake-catcher.
- Explicit dependency lines for all library and application objects.

Important behavior:
- `configure` replaces `@...@` placeholders to produce a concrete Makefile.
- Supports plain `.o`/`.a` builds and libtool `.lo`/`.la` builds.
- Supports optional `ansi2knr` conversion for K&R compilers.
- Builds sample apps against `libjpeg.$(A)`.
- `test` performs encode/decode/transcode regression checks against bundled test images with `cmp`.
- `jconfig.h` target deliberately fails with installation instructions if configuration was not prepared.

Dependencies:
- IJG source tree, configured `jconfig.h`, system memory manager selection, optional libtool, optional `ansi2knr`, POSIX make tools.
