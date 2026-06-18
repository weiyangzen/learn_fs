# sources/user-network-fs/libsmb2/include/amiga_os/config.h

## Purpose
This generated-style `config.h` snapshot configures libsmb2 for Amiga OS targets.

## Important APIs, Types, and Functions
It defines feature macros such as `CONFIGURE_OPTION_TCP_LINGER`, header availability, `HAVE_SOCKADDR_LEN`, package identity, and version strings. GSSAPI/Kerberos, `HAVE_LINGER`, `HAVE_POLL_H`, `HAVE_SYS_POLL_H`, and `HAVE_SOCKADDR_STORAGE` are disabled in this variant.

## Control Flow
There is no direct control flow. The macros steer conditional compilation in socket, auth, endian, and compatibility code.

## State and Persistence Behavior
No state is persisted. Compile-time state is fixed by macros and affects binary capabilities.

## Dependencies and Integration Points
It integrates with code guarded by `HAVE_*` macros, especially network address handling, polling support, and auth provider selection. Package macros report libsmb2 `4.0.0`.

## Risks and Edge Cases
Disabling poll and sockaddr storage forces alternate code paths that need platform coverage. GSSAPI is unavailable, so authentication falls back to non-Kerberos mechanisms. Generated comments may not match a current configure run if platform headers change.

## Test Signals
Cross-compile on the Amiga target, run connection tests without poll support, and verify address iteration, linger behavior, and NTLM authentication.
