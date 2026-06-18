<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/configure.ac -->
# sources/user-network-fs/cifs-utils/configure.ac

## Purpose

`configure.ac` is the Autoconf entry point for cifs-utils. It defines package metadata, feature toggles, install paths, dependency checks, compatibility probes, Automake conditionals, and generated configuration files.

## Important APIs, Types, and Functions

Important macros include `AC_INIT`, `AC_CONFIG_SRCDIR`, `AC_CONFIG_HEADERS`, `AC_CONFIG_FILES`, `AM_INIT_AUTOMAKE`, feature `AC_ARG_ENABLE` blocks, `AC_ARG_WITH(idmap-plugin)`, `AC_ARG_WITH(pamdir)`, `AC_ARG_VAR(ROOTSBINDIR)`, compiler/header/function checks, `AC_TEST_WBCHL`, `AC_TEST_WBC_IDMAP_BOTH`, `LIBCAP_NG_PATH`, `AC_LIBCAP`, and `AM_CONDITIONAL` definitions.

## Control Flow

Configure starts by capturing feature choices with default `"maybe"`. It verifies compiler and libc facilities, requires `setfsuid`, `talloc`, and common headers/functions, then conditionally checks Kerberos/GSSAPI/keyutils/PAM/wbclient/manpage tooling. Missing optional dependencies disable features unless the user forced `--enable-...=yes`, in which case configure errors. The final conditionals drive `Makefile.am`.

## State and Persistence Behavior

It writes `config.h`, generated Makefiles, substituted variables such as `pluginpath`, `pamdir`, `PIE_CFLAGS`, `RELRO_CFLAGS`, `KRB5_LDADD`, `GSSAPI_LDADD`, and feature macros such as `HAVE_KRB5_KEYBLOCK_KEYVALUE` and `ENABLE_SYSTEMD`.

## Dependencies and Integration Points

It integrates with local `aclocal` macros for wbclient and capabilities, docutils `rst2man`, Kerberos variants, keyutils, PAM headers, libtalloc, libresolv through Makefile link settings, and Automake conditional sections.

## Risks and Edge Cases

Default `"maybe"` behavior can hide missing optional utilities in developer builds. PIE/RELRO flags are applied without probing compiler/linker support. The `ROOTSBINDIR` empty test is unquoted. Kerberos compatibility probes must remain consistent with `cifs.upcall.c` macro branches.

## Test Signals

Run configure matrices with all optional dependencies present, absent, and forced enabled. Validate `config.h` macro choices for MIT and Heimdal Kerberos, wbclient BOTH support, libcap-ng versus libcap fallback, and manpage generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/configure.ac -->
