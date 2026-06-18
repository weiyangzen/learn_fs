# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convTR2M.c

This file packs a `Ticketreq` into plain auth protocol bytes.

Key behavior:
- `convTR2M` serializes ticket request fields without encryption.

Important details:
- Complements `convM2TR`.
