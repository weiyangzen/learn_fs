<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/meson.build -->
# sources/user-network-fs/ksmbd-tools/control/meson.build

## Purpose

Build-system description for the `control Meson` component in ksmbd-tools.

## Important APIs, Types, and Functions

Creates static library `control` from `control.c`, renders `ksmbd.control.8`, and installs the control symlink.

## Control Flow

Configures compile-time path defines, builds against GLib, configures the man page, then installs a symlink to libexec `ksmbd.tools`.

## State and Persistence Behavior

Static library in build tree and man/symlink in install tree.

## Dependencies and Integration Points

Top-level include dirs, GLib, in_data, and runstatedir.

## Risks and Edge Cases

Runtime sysfs control paths are fixed in C; build only controls config/run paths. Symlink install target must match where tools subdir installs `ksmbd.tools`.

## Test Signals

Meson compile and install smoke test of the symlink.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/meson.build -->
