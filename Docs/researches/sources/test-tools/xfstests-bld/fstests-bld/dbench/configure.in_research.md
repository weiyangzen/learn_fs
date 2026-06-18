# sources/test-tools/xfstests-bld/fstests-bld/dbench/configure.in

Purpose: Autoconf input for configuring dbench portability features and Makefile generation.

Important APIs and functions: uses compiler/install/header checks, `_GNU_SOURCE` definition, library searches for `getxattr`, `socket`, and `gethostbyname`, extensive xattr/EA function checks, snprintf/asprintf checks, and `va_copy`/`__va_copy` probes.

Control flow: configures compiler flags, detects headers and functions, defines `HAVE_EA_SUPPORT` if any file-descriptor xattr API exists, defines `HAVE_VA_COPY` or `HAVE___VA_COPY`, then outputs `Makefile`.

State and persistence: generated artifacts include `configure`, `config.h`, and substituted `Makefile`.

Dependencies and integration: consumed by `autoconf`/`autoheader` and invoked by `build-all` before compiling dbench.

Risks: uses older Autoconf macros such as `AC_TRY_LINK`; modern Autoconf may warn. EA detection is broad and may enable code paths with partial platform support.

Test signals: configure completes, `config.h` reflects detected APIs, and dbench builds against the selected libraries.
