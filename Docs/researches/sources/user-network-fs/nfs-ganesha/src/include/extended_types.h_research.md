# sources/user-network-fs/nfs-ganesha/src/include/extended_types.h

## Purpose
`extended_types.h` supplies platform-dependent type compatibility definitions used by older Ganesha code and filesystem interfaces.

## Important APIs, Types, And Functions
It includes generated `config.h`, then includes OS-specific extended type headers for Linux or FreeBSD. It defines `longlong_t`, `u_longlong_t`, `uint_t`, and maps missing `ENOATTR` to `ENODATA`.

## Control Flow
All behavior is preprocessor selection. `LINUX` and `FREEBSD` macros from generated config choose the OS-specific include path. If `ENOATTR` is unavailable, the fallback macro is defined.

## State And Persistence
No runtime state or persistence exists. The header affects compile-time type names and errno compatibility.

## Dependencies And Integration Points
It depends on `config.h`, `<sys/types.h>`, and OS-specific headers under `os/linux` or `os/freebsd`. It integrates with FSAL and xattr-facing code that expects Solaris/BSD-style type names or `ENOATTR`.

## Risks
Mapping `ENOATTR` to `ENODATA` overlays errno semantics on Linux, which is intentional but can surprise code that distinguishes them elsewhere. Unsupported OS macros may skip platform headers. Type aliases may conflict if platform headers define them differently.

## Test Signals
Build tests on Linux and FreeBSD are the main signal. Compile checks should verify the aliases and `ENOATTR` availability, and xattr tests should validate expected no-attribute error mapping.
