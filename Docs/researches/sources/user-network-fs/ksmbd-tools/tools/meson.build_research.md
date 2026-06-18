# sources/user-network-fs/ksmbd-tools/tools/meson.build

## Purpose

`tools/meson.build` is the Meson build definition for `ksmbd.tools`. It declares the common source list, conditionally adds SPNEGO/Kerberos implementation files when `krb5_dep` is found, sets path defines, links command-specific internal libraries, and installs the resulting libexec executable.

## Important APIs, Types, and Functions

Important Meson objects are `ksmbd_tools_files`, `executable('ksmbd.tools', ...)`, `include_dirs`, `glib_dep`, `krb5_dep`, `asn1_lib`, `pthread_lib`, and link targets `addshare_lib`, `adduser_lib`, `control_lib`, and `mountd_lib`.

## Control Flow

At configuration time Meson checks `krb5_dep.found()`. At build time it compiles the selected files and links the executable. Runtime control remains in `tools.c`.

## State and Persistence Behavior

No runtime state. Build-time persistence is the source list, `SYSCONFDIR`, `RUNSTATEDIR`, dependency graph, and installation directory.

## Dependencies and Integration Points

It must match the Autotools source selection in `Makefile.am`. It also integrates the project-level `asn1_lib` dependency while the local ASN.1 source is included only for krb5-enabled builds.

## Risks and Edge Cases

Differences from `Makefile.am` can alter behavior across build systems. Passing `krb5_dep` in dependencies even when not found depends on Meson's dependency object semantics. Optional Kerberos source selection must keep headers and symbols consistent.

## Test Signals

Run Meson configure/build on Linux with krb5 present and absent, inspect `ksmbd.tools` link dependencies, and verify installed libexec path.
