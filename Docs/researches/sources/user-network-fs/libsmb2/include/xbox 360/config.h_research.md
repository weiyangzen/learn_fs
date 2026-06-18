# sources/user-network-fs/libsmb2/include/xbox 360/config.h

## Purpose
This generated-style `config.h` snapshot configures libsmb2 for Xbox 360 builds.

## Important APIs, Types, and Functions
It enables `HAVE_ERRNO_H`, `HAVE_FCNTL_H`, `HAVE_LINGER`, `HAVE_STDINT_H`, `HAVE_STDIO_H`, `HAVE_STDLIB_H`, `HAVE_STRING_H`, `HAVE_SYS_STAT_H`, `HAVE_SYS_TYPES_H`, and `HAVE_TIME_H`. It disables POSIX socket, poll, uio, unistd, netdb, GSSAPI/Kerberos, sockaddr length, and sockaddr storage macros.

## Control Flow
No runtime control flow exists. The macros steer compilation into Xbox-specific compatibility paths.

## State and Persistence Behavior
No state is persisted. Compile-time feature state controls the resulting binary.

## Dependencies and Integration Points
It integrates with Xbox headers and `portable-endian.h`'s Windows/Xbox branch, plus `asprintf.h`'s `_XBOX` handling.

## Risks and Edge Cases
The directory path contains a space, which can break scripts that do not quote paths. Disabled socket/storage macros require Xbox-specific socket typedefs and APIs to be used correctly.

## Test Signals
Cross-compile with path quoting, run basic URL parse/connect/stat/read/write tests, and verify `_XBOX` formatting and endian branches.
