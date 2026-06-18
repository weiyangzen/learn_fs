# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convA2M.c

This file packs an `Authenticator` into auth protocol bytes.

Key behavior:
- `convA2M` serializes numeric fields and strings, then encrypts the payload with the supplied DES key.

Important details:
- Uses local macros for little-endian field emission.
- Returns the fixed authenticator message size.
