# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2PR.c

This file unpacks encrypted auth protocol bytes into a `Passwordreq`.

Key behavior:
- `convM2PR` decrypts the message and extracts password-change request fields.

Important details:
- Uses fixed authsrv field layout and little-endian macros.
