# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/auth.h

## Purpose
Defines the telnet authentication method interface and result levels.

## Main Interfaces
Defines authentication status constants from reject through valid. Defines `Authenticator`, a method table with type, way, init/send/is/reply/status/printsub function pointers. Includes `auth-proto.h`.

## Other Definitions
Defines credential forwarding option flags and declares `auth_debug_mode`.

## Dependencies
Depends on telnet authentication constants from the including context and method implementations matching the function pointer signatures.

## Risks And Notes
The `Authenticator` structure is the central ABI between the generic auth dispatcher and Kerberos/SRA backends.
