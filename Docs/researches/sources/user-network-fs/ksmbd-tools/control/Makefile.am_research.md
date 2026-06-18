<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/Makefile.am -->
# sources/user-network-fs/ksmbd-tools/control/Makefile.am

## Purpose

Build-system description for the `control autotools` component in ksmbd-tools.

## Important APIs, Types, and Functions

Defines `libcontrol.a` from `control.c`, renders `ksmbd.control.8`, and installs an sbindir symlink to `ksmbd.tools`.

## Control Flow

The library is linked into the multi-call tool; the generated man page and symlink are installed by standard automake targets plus hooks.

## State and Persistence Behavior

Install state is symlink and man page only.

## Dependencies and Integration Points

Uses configured sysconfdir/runstatedir defines and GLib/libnl/common include flags.

## Risks and Edge Cases

control.c uses sysfs and runstatedir paths at runtime, so build-time substitutions must match installed service paths.

## Test Signals

Autotools build and install smoke test; `ksmbd.control --help` should work without kernel support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/Makefile.am -->
