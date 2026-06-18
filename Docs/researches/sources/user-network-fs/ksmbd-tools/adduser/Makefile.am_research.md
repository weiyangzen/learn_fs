<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/Makefile.am -->
# sources/user-network-fs/ksmbd-tools/adduser/Makefile.am

## Purpose

Build-system description for the `adduser autotools` component in ksmbd-tools.

## Important APIs, Types, and Functions

Defines `libadduser.a` from password hashing, user administration, CLI, and headers; renders `ksmbd.adduser.8`; installs `ksmbd.adduser` as a symlink to `ksmbd.tools`.

## Control Flow

Builds the static library and generated man page, then uses install/uninstall hooks to keep the command symlink current.

## State and Persistence Behavior

Install state is the man page and symlink. Password database state is handled by runtime code, not the build file.

## Dependencies and Integration Points

Depends on GLib, libnl flags, common includes, generated config macros, and source parity with Meson.

## Risks and Edge Cases

The MD4 and password-database source files must stay included in both build systems. Symlink dispatch can fail if the shared binary is not installed.

## Test Signals

Autotools compile, distcheck, DESTDIR install, and CLI smoke tests for `--help` and `--version`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/Makefile.am -->
