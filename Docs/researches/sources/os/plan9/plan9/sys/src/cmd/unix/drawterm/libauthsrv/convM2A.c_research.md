# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2A.c

This file unpacks encrypted auth protocol bytes into an `Authenticator`.

Key behavior:
- `convM2A` decrypts with the supplied key and decodes fields into an `Authenticator`.

Important details:
- Uses little-endian extraction macros matching `convA2M`.
