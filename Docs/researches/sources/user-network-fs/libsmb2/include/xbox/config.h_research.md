# sources/user-network-fs/libsmb2/include/xbox/config.h

## Purpose
This generated-style `config.h` snapshot configures libsmb2 for original Xbox builds.

## Important APIs, Types, and Functions
It enables stdio/stdlib/string/sys types/stat/time, `HAVE_ERRNO_H`, `HAVE_FCNTL_H`, `HAVE_LINGER`, and `HAVE_SOCKADDR_STORAGE`, but disables `HAVE_STDINT_H`, POSIX socket/poll/uio/unistd/netdb, GSSAPI, and Kerberos.

## Control Flow
No runtime logic exists. Macros control compile-time portability branches for Xbox.

## State and Persistence Behavior
No runtime persistence. Feature state is fixed at compile time.

## Dependencies and Integration Points
It integrates with Xbox socket headers from `libsmb2.h`, `_XBOX` support in `portable-endian.h`, and `asprintf.h`.

## Risks and Edge Cases
`HAVE_STDINT_H` is disabled while much of the public API uses fixed-width integer types; compatibility headers must provide them. GSSAPI/Kerberos is unavailable. Differences from the Xbox 360 config need target-specific testing.

## Test Signals
Compile public headers in a downstream Xbox sample, run endian/formatting smoke tests, and exercise basic SMB connect and file metadata operations.
