# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2T.c

This file unpacks encrypted auth protocol bytes into a `Ticket`.

Key behavior:
- `convM2T` decrypts the ticket and extracts ticket fields.

Important details:
- Complements `convT2M`.
