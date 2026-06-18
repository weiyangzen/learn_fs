# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/headers.h

Central include header for Aquarela SMB/NetBIOS C files.

Contents:
- Includes Plan 9 system headers: `u.h`, `libc.h`, `ip.h`, `thread.h`, `auth.h`, and `regexp.h`.
- Includes project headers: `netbios.h`, `smb.h`, `smbdat.h`, and `smbfns.h`.

Interactions:
- Most SMB server files include this instead of listing all dependencies individually.

Notable details:
- Keeps protocol constants, shared structs, and prototypes in one compilation include path.
