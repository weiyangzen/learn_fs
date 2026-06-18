<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/meson.build -->
# sources/user-network-fs/ksmbd-tools/addshare/meson.build

## Purpose

Build-system description for the `addshare Meson` component in ksmbd-tools.

## Important APIs, Types, and Functions

Creates static library `addshare`, compiles `share_admin.c`, `addshare.c`, and header, renders `ksmbd.addshare.8`, and installs the command symlink to the shared libexec binary.

## Control Flow

Meson applies component path defines, links against GLib, configures the man page from `in_data`, and installs the symlink.

## State and Persistence Behavior

Build-tree static library and generated man page; install-tree man page and symlink.

## Dependencies and Integration Points

Consumes top-level `include_dirs`, `glib_dep`, `runstatedir`, and `in_data`.

## Risks and Edge Cases

Path expression behavior depends on Meson option values. Build parity with Makefile.am is required.

## Test Signals

Meson compile, install into DESTDIR, and compare generated command/man artifacts with autotools.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/meson.build -->
