# sources/user-network-fs/samba/source3/lib/version.c

## Purpose
This file exposes compiled Samba version and copyright strings through tiny function wrappers.

## Important APIs and Functions
`samba_version_string` returns `SAMBA_VERSION_STRING`; `samba_copyright_string` returns `SAMBA_COPYRIGHT_STRING`.

## Control Flow and State
Both functions return static compile-time strings and have no control-flow complexity or state.

## Dependencies and Integration Points
It includes `version.h`, where the generated or configured version macros are defined. Consumers use these wrappers for diagnostics, command output, and tests.

## Risks and Test Signals
Risk is build configuration drift rather than runtime behavior. Tests should assert non-null returned strings and that `version_test` prints the configured version string.
