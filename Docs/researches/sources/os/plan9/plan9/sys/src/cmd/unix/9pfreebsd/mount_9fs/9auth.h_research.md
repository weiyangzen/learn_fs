# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/9auth.h

Read fully: 159 lines, 4612 bytes. SHA-256 prefix: `d9c295f96404fa17`.

This header defines legacy Plan 9 authentication constants, wire structures, and prototypes for the FreeBSD 9FS mount utility.

Definitions include:
- Length constants for DES keys, challenges, domains, secrets, APOP, MD5, and key database entries.
- Auth message numbers such as `AuthTreq`, `AuthChal`, `AuthOK`, `AuthErr`, `AuthTs`, `AuthTc`, `AuthAs`, and `AuthAc`.
- Wire structs `Ticketreq`, `Ticket`, `Authenticator`, `Passwordreq`, `Nvrsafe`, `Chalstate`, `Apopchalstate`, `Chapreply`, and `MSchapreply`.
- Conversion/authentication function prototypes for tickets, authenticators, password requests, challenge/response, login, and SSL negotiation.

Integration: `crypt.c` uses `U9AUTH_DESKEYLEN`; `mount_9fs.c` uses `passtokey()`-compatible DES key material and auth constants.

Risk notes: these are old DES-era Plan 9 auth formats and not modern cryptographic interfaces.
