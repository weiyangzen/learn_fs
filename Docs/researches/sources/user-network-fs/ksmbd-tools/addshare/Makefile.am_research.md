<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/Makefile.am -->
# sources/user-network-fs/ksmbd-tools/addshare/Makefile.am

## Purpose

Build-system description for the `addshare autotools` component in ksmbd-tools.

## Important APIs, Types, and Functions

Defines `libaddshare.a` from `share_admin.c`, `addshare.c`, and `share_admin.h`, installs the generated `ksmbd.addshare.8` man page, and creates an sbindir symlink named `ksmbd.addshare` to the shared `ksmbd.tools` executable.

## Control Flow

Automake builds a noinst static library, renders the man page through `in_script`, then install hooks replace any old symlink and create the new command entry point.

## State and Persistence Behavior

Install state is the generated man page and the symlink. No runtime data is owned here.

## Dependencies and Integration Points

Uses GLib flags, libnl flags through common AM_CFLAGS, top-level include paths, and configure substitutions for sysconfdir and runstatedir.

## Risks and Edge Cases

The CLI is a symlink into a multi-call binary, so symlink target and `set_tool_main` dispatch must agree. Static library source lists must match Meson.

## Test Signals

Autotools build, install into DESTDIR, verify man page generation and that `ksmbd.addshare --help` dispatches correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/Makefile.am -->
