# sources/user-network-fs/libsmb2/examples/Makefile.am

Purpose: This Automake file builds the example programs for autotools builds.

Important APIs and types: It defines `noinst_PROGRAMS`, `AM_CPPFLAGS`, `COMMON_LIBS`, and per-program `_LDADD` variables. It compiles with include paths for `include` and `include/smb2`, `_U_=__attribute__((unused))`, `-Wall`, and `-Werror`.

Control flow: Automake builds each listed example as a non-installed executable and links it to `../lib/libsmb2.la`.

State and persistence behavior: Outputs are local example binaries in the build tree; they are not installed.

Dependencies and integration points: It integrates with the libtool library target from `lib/Makefile.am` and exercises examples for cat, put, ls, epoll, raw stat/fsstat/getsd, readlink, LSA, seek, share enum/info, stat/statvfs, truncate, rename, CMD-FIND, server, and notify.

Risks: The autotools list is broader than the CMake list, so a source can compile under one build system but not the other. `-Werror` makes examples sensitive to compiler warning drift and platform-specific warnings.

Test signals: `./configure --enable-examples && make` is the primary signal. A cross-check against CMake `ENABLE_EXAMPLES` catches missing example wiring.
