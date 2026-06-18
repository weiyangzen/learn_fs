<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/meson.build -->
# sources/user-network-fs/ksmbd-tools/adduser/meson.build

## Purpose

Build-system description for the `adduser Meson` component in ksmbd-tools.

## Important APIs, Types, and Functions

Creates static library `adduser` from MD4, user admin, CLI, and headers; renders `ksmbd.adduser.8`; installs the `ksmbd.adduser` symlink.

## Control Flow

Applies compile-time sysconfdir/runstatedir defines, depends on GLib, configures the man page, and creates a symlink to `ksmbd.tools`.

## State and Persistence Behavior

Build outputs are the static library and man page; install outputs are the man page and symlink.

## Dependencies and Integration Points

Uses top-level include dirs, GLib dependency, in_data, and runstatedir.

## Risks and Edge Cases

The password hashing file must remain in the library. Meson and automake source lists must not diverge.

## Test Signals

Meson compile/dist and CLI smoke tests for password command dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/meson.build -->
