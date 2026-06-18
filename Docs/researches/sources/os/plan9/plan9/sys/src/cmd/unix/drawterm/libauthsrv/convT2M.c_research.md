# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convT2M.c

This file packs a `Ticket` into encrypted auth protocol bytes.

Key behavior:
- `convT2M` serializes ticket fields and encrypts with the supplied key.

Important details:
- Complements `convM2T`.
