# sources/user-network-fs/libsmb2/include/ps3/config.h

## Purpose
This generated-style `config.h` snapshot configures libsmb2 for PS3 builds.

## Important APIs, Types, and Functions
It enables `HAVE_ERRNO_H`, `HAVE_FCNTL_H`, `HAVE_LINGER`, `HAVE_NETINET_IN_H`, `HAVE_STDINT_H`, `HAVE_STDIO_H`, `HAVE_STDLIB_H`, `HAVE_STRING_H`, `HAVE_SYS_TYPES_H`, `HAVE_TIME_H`, and `HAVE_UNISTD_H`. It disables GSSAPI/Kerberos, poll, most socket/stat/uio sys headers, sockaddr length/storage, and netdb.

## Control Flow
No runtime control flow. Compile-time branches use these feature flags.

## State and Persistence Behavior
No persisted state. The generated macros define platform capabilities for the resulting binary.

## Dependencies and Integration Points
It integrates with PS3 platform networking and `portable-endian.h`'s big-endian PS3 branch. Kerberos is unavailable.

## Risks and Edge Cases
Several socket/sys headers are disabled while networking is still required, so PS3-specific compatibility code must cover all needed types and calls. Big-endian conversion paths require explicit testing.

## Test Signals
Cross-compile for PS3, run basic connect/share/stat tests, and verify endian-correct SMB header and payload fields on the wire.
