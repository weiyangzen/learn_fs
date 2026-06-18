<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/version.h -->
# sources/user-network-fs/ksmbd-tools/include/version.h

## Purpose

Single-source version header for both build systems and runtime version output.

## Important APIs, Types, and Functions

Defines `KSMBD_TOOLS_VERSION` as `3.5.3`.

## Control Flow

configure.ac and meson.build parse this macro to set project/package version; tools code uses it for `--version` and template substitution.

## State and Persistence Behavior

No runtime state.

## Dependencies and Integration Points

Integrated by autotools, Meson, and man-page/unit template generation.

## Risks and Edge Cases

Version extraction depends on the macro spelling and quote format.

## Test Signals

Tests should verify `./configure --version`, Meson project version, generated man pages, and `ksmbd.* --version` all agree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/version.h -->
