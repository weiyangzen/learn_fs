# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ltconfig

Purpose: GNU libtool 1.2 configure-time generator that probes the host toolchain and creates a system-specific `libtool` script.

Key contents:
- Shell script with GPL/libtool exception header.
- Parses options such as `--disable-shared`, `--disable-static`, `--srcdir`, `--no-verify`, `--with-gcc`, `--with-gnu-ld`, and `--silent`.
- Locates and uses `config.guess`/`config.sub` unless host verification is disabled.
- Detects `ranlib`, C compiler, GCC status, PIC flags, static-link flags, symlink support, linker path, GNU ld status, `nm`, and global-symbol parsing pipeline.
- Contains per-OS linker/shared-library rules for AIX, AmigaOS, FreeBSD, HP-UX, IRIX, NetBSD, OpenBSD, OS/2, OSF, SCO, Solaris, SunOS, UnixWare, UTS, Linux ELF, and related variants.
- Computes shared library naming, soname, runtime path variables, install finish commands, archive commands, hardcoding behavior, and object directory.
- Writes a configured `libtool` script containing discovered variables, then appends `ltmain.sh`.

Important behavior:
- Defaults to static archive support and shared-library support when possible.
- Falls back to static-only behavior if compiler/linker/PIC/dynamic-linker tests fail.
- Stores probe output in `config.log`.
- Quotes generated shell variables carefully before embedding them in the generated script.
- Does not build JPEG code directly; it supports `makefile.cfg` when libtool builds are requested.

Dependencies:
- POSIX shell utilities, compiler/linker tools, `config.guess`, `config.sub`, and `ltmain.sh`.
