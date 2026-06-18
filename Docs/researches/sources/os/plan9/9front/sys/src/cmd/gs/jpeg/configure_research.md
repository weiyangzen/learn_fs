# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/configure

Autoconf 2.12-generated configuration script for the IJG JPEG subtree.

Key points:
- Parses standard Autoconf directory, host/build/target, program-transform, cache, quiet, site, `--with-*`, and `--enable-*` options.
- Package-specific help covers `--enable-shared`, `--enable-static`, and `--enable-maxmem[=N]`; `--with-maxmem` remains supported for compatibility with older IJG releases.
- Locates source directory by checking for `jcmaster.c`, loads site scripts, opens `config.log`, normalizes locale variables, and builds `confdefs.h`.
- Detects C compiler (`gcc` then `cc`), compiler usability/cross status, GNU C, C preprocessor, function prototypes, standard headers, string header style, `size_t`, unsigned char/short, `void`, working `const`, inline spelling, incomplete-type behavior, short external names, signedness of `char`, signed right shifts, and whether `fopen` accepts binary `b` mode.
- Finds `install-sh`/`install.sh`, chooses a BSD-compatible install program, detects `ranlib`, and optionally configures GNU libtool for shared/static builds.
- Selects JPEG memory manager: default `jmemnobs.$(O)`, `jmemansi.$(O)` when temp-file support and `tmpfile()` are available, or `jmemname.$(O)` with `NEED_SIGNAL_CATCHER` and optional `NO_MKTEMP`.
- Extracts `JPEG_LIB_VERSION` from `jpeglib.h`.
- Sets substitutions controlling `ansi2knr` use, libtool comments, forced shared-library install, include flags, object/archive suffixes, link command, install commands, memory manager, and generated headers.
- Writes `config.status`, which generates `Makefile` from `makefile.cfg` and `jconfig.h` from `jconfig.cfg` using sed substitution fragments.

Dependencies and interactions:
- Consumes `makefile.cfg`, `jconfig.cfg`, `jpeglib.h`, optional `ltconfig`/`ltmain.sh`, and the install helper.
- Its generated `jconfig.h` controls the same compile-time feature gates read by `cdjpeg.h`, `cderror.h`, `cjpeg.c`, `djpeg.c`, memory managers, and library internals.

Risk notes:
- This is very old Autoconf output; it uses temporary files, generated shell code, legacy option spellings, and historical compiler probes that may not represent modern platforms cleanly.
- Cross-compiling paths assume signed `char`, signed right shift, and working binary `fopen` unless overridden, which may produce subtly wrong `jconfig.h`.
- `--enable-maxmem` accepts only numeric megabytes and converts to bytes with `expr`; malformed values are rejected, but very large values depend on shell/arithmetic limits.
