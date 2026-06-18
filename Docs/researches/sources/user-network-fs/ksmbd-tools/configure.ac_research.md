<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/configure.ac -->
# sources/user-network-fs/ksmbd-tools/configure.ac

## Purpose

Autoconf entry point for ksmbd-tools. It discovers compiler, dependency, installation, runtime-directory, systemd, pthread, GLib, libnl, and optional Kerberos capabilities.

## Important APIs, Types, and Functions

Defines project metadata from `include/version.h`, substitutes `ksmbd_tools_version`, `in_script`, `runstatedir`, `systemdsystemunitdir`, and `PTHREAD_LIBS`, and emits `config.h`. Important options are `--enable-krb5`, `--with-rundir`, and `--with-systemdsystemunitdir`.

## Control Flow

After base tool checks it resolves krb5 only when enabled, probes krb5 headers and ABI differences, requires GLib and libnl/libnl-genl, finds pthread support, and configures Makefiles for root, addshare, adduser, control, mountd, and tools.

## State and Persistence Behavior

Persists feature results as config.h macros such as `CONFIG_KRB5`, `HAVE_KRB5_AUTH_CON_GETRECVSUBKEY`, `HAVE_KRB5_KEYBLOCK_KEYVALUE`, `HAVE_KRB5_AUTHENTICATOR_CLIENT`, and `HAVE_KRB5_AUTH_CON_GETAUTHENTICATOR_DOUBLE_POINTER`.

## Dependencies and Integration Points

Consumes pkg-config modules `glib-2.0`, `libnl-3.0`, `libnl-genl-3.0`, optional `krb5`, optional systemd, and m4/autotools macros.

## Risks and Edge Cases

Kerberos support is off by default, and optional mode can silently disable support if headers are missing. ABI probes must stay aligned with both MIT and Heimdal. `runstatedir` fallback behavior affects lock and fifo paths.

## Test Signals

Configure and distcheck with krb5 disabled, MIT krb5 enabled, and Heimdal krb5 enabled. Inspect config.h and generated template substitutions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/configure.ac -->
