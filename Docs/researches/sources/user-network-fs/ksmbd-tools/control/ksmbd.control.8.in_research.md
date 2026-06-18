<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/ksmbd.control.8.in -->
# sources/user-network-fs/ksmbd-tools/control/ksmbd.control.8.in

## Purpose

Manual-page template for `ksmbd.control` and its runtime control of mountd and kernel ksmbd behavior.

## Important APIs, Types, and Functions

Documents command synopsis, options, default paths, version/help behavior, and related files/utilities. Build systems substitute version, sysconfdir, sbindir, and runstatedir where present.

## Control Flow

The template is transformed into a man page during autotools or Meson builds. It describes the CLI control flow implemented in the matching C file.

## State and Persistence Behavior

No runtime state, but it documents persistent files, lock/fifo paths, kernel sysfs control, or daemon behavior depending on the command.

## Dependencies and Integration Points

Integrated with build template substitution and the matching CLI source.

## Risks and Edge Cases

The man page can drift from getopt options, default limits, and runtime behavior. Generated paths must match compile-time macros.

## Test Signals

Tests should compare documented options with getopt tables and verify generated man-page substitution in both build systems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/ksmbd.control.8.in -->
