# sources/user-network-fs/ksmbd-tools/tools/Makefile.am

## Purpose

`tools/Makefile.am` is the Autotools build definition for the `ksmbd.tools` libexec binary. It lists shared management/config source files, conditionally includes Kerberos/SPNEGO support, and links the command-specific static libraries that provide addshare, adduser, control, and mountd entry points.

## Important APIs, Types, and Functions

The important build variables are `AM_CFLAGS`, `LIBS`, `libexec_PROGRAMS`, `ksmbd_tools_SOURCES`, and `ksmbd_tools_LDADD`. The `HAVE_LIBKRB5` conditional adds `management/spnego.c`, `asn1.c`, `management/spnego_krb5.c`, and `management/spnego_mech.h`.

## Control Flow

There is no runtime control flow. At build generation time Automake expands this file, compiles the listed shared sources into `ksmbd.tools`, and links the tool-specific archives. At runtime `tools.c` dispatches based on the executable basename.

## State and Persistence Behavior

No runtime state is stored here. The file persists build policy: include paths, defines for `SYSCONFDIR` and `RUNSTATEDIR`, feature-gated Kerberos sources, and linked libraries.

## Dependencies and Integration Points

The build integrates GLib, libnl, optional libkrb5, pthreads, top-level include headers, and static libraries from sibling directories. It must remain consistent with `tools/meson.build` so both build systems expose the same feature surface.

## Risks and Edge Cases

Source-list drift between Autotools and Meson can produce different binaries. Optional Kerberos compilation depends on `HAVE_LIBKRB5`; missing the ASN.1/SPNEGO files when krb5 is enabled would break authentication symbols.

## Test Signals

Run an Autotools build with and without libkrb5 detected, check that `ksmbd.tools` links, and verify each symlink/basename mode starts correctly.
