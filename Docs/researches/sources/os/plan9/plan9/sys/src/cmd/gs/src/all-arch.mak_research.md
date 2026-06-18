# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/all-arch.mak

This is a historical multi-architecture wrapper makefile for building Ghostscript across many Unix/RISC targets without editing the main Unix makefiles.

Core responsibilities:
- Defines common wrapper variables for generated/object directories, source roots, Ghostscript library paths, install directories, and extra devices.
- Uses either `src/unixansi.mak` or `src/unix-gcc.mak` via `ARGS`/`ARGSGCC`.
- Enables installed shared libpng and zlib by default through `SHARE_LIBPNG=1` and `SHARE_ZLIB=1`.
- Provides convenience targets for standard make operations, install variants, fontmap replacement, and `pdf_sec.ps` replacement.
- Provides per-platform targets for Rhapsody, DEC OSF, Ultrix, HP-UX, AIX, Linux, NeXT, IRIX, Solaris, and SunOS, with compiler flags and X11/library paths tailored to each.
- Contains optional GNU readline targets that add `gnrdline.dev` and termcap linkage.

Notable details:
- It embeds University of Utah local paths and host-oriented convenience aliases.
- Many targets work around specific compiler bugs or ABI requirements, such as MIPSpro optimization issues and AIX `gp_unix.o` POSIX visibility.
- It is infrastructure for portability and reproducible legacy builds, not runtime code.
- Filesystem relevance is limited to install/copy/link operations and Ghostscript runtime search-path definitions.
