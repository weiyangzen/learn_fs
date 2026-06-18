# sources/user-network-fs/libsmb2/configure.ac

Purpose: This is the autotools configuration source for libsmb2. It declares package metadata, feature flags, compiler/linker setup, portability checks, and generated Makefiles.

Important APIs and types: It uses `AC_INIT`, `AC_PREREQ`, `AC_CONFIG_HEADERS`, `AM_INIT_AUTOMAKE`, `AC_CANONICAL_HOST`, `AC_PROG_CC`, `LT_INIT`, `AC_ARG_ENABLE`, `AC_ARG_WITH`, `AC_DEFINE`, `AC_CHECK_HEADERS`, `AC_CHECK_LIB`, `AC_CHECK_MEMBER`, `AM_CONDITIONAL`, `AC_SUBST`, and `AC_CONFIG_FILES`.

Control flow: The script initializes package version 6.1.0, sets up Automake/libtool, forces `_FILE_OFFSET_BITS=64`, handles `--enable-examples`, handles `--without-libkrb5`, handles TCP linger behavior, builds warning flags with optional `-Werror`, handles Solaris and Windows socket libraries, requires `libdl`, checks headers and socket struct members, then generates root/examples/include/lib/tests/utils Makefiles and `libsmb2.pc`.

State and persistence behavior: Generated state includes `configure`, `config.h`, Makefiles, libtool files, substituted variables such as `MAYBE_LIBKRB5`, `WARN_CFLAGS`, and `LIBSOCKET`, and conditional build directories.

Dependencies and integration points: This file drives the autotools build used by `bootstrap`, `Makefile.am`, examples, tests, utilities, and pkg-config generation. It overlaps with the CMake configure checks and must remain semantically aligned.

Risks: Kerberos support is enabled by default and errors out if GSSAPI headers are missing unless disabled. `AC_CHECK_LIB([dl], [dlsym])` makes libdl mandatory, which can be awkward on systems where dlsym is in libc or unavailable. The CMake and autotools feature checks are not perfectly equivalent, creating risk of divergent builds.

Test signals: `./bootstrap && ./configure`, `./configure --without-libkrb5`, `./configure --enable-examples`, `make`, `make test`, and host-specific builds for Windows/Solaris are the main validation signals.
