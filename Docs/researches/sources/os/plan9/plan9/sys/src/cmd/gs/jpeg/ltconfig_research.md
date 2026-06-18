# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ltconfig

This is GNU libtool 1.2's `ltconfig` generator script. It creates a host-specific `libtool` script by probing compiler, linker, archive, symbol, shared-library, and runtime-linker behavior, then appending `ltmain.sh`.

The script parses options such as `--disable-shared`, `--disable-static`, `--srcdir`, `--no-verify`, `--with-gcc`, and `--with-gnu-ld`. It verifies or guesses the host through `config.guess` and `config.sub`, sets up logging in `config.log`, and normalizes shell behavior for echo, locale, and quoting.

Compiler probing discovers `gcc` or `cc`, detects whether the compiler is GNU C, selects PIC flags, checks static-link flags, and tests whether the chosen PIC flag actually compiles. It also finds `ranlib`, `ld`, `nm`, and `ln -s` behavior.

Linker probing determines whether shared libraries can be built and fills platform-specific command templates for AIX, AmigaOS, FreeBSD, HP-UX, IRIX, NetBSD, OpenBSD, OS/2, OSF, SCO, Solaris, SunOS, UnixWare, UTS, GNU/Linux, and related systems. It computes hardcoding behavior for library paths and dynamic linker characteristics such as library naming, soname patterns, runtime path variables, and install finishing commands.

The script tests an `nm` symbol extraction pipeline by compiling and linking a small program. If successful, the generated libtool can support symbol preloading/dlpreopen features.

At the end, it quotes all discovered variables, writes the generated `libtool` shell script with configuration variables such as `build_libtool_libs`, `archive_cmds`, `library_names_spec`, `shlibpath_var`, and `hardcode_action`, then appends `ltmain.sh`.

This file is build infrastructure for the bundled JPEG package. Its security-sensitive surface is shell execution during configure/build time: it creates and runs compiler/linker test commands and writes `libtool`.
