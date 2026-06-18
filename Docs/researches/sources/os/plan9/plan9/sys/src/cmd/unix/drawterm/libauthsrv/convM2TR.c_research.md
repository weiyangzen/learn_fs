# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2TR.c

This file unpacks plain auth protocol bytes into a `Ticketreq`.

Key behavior:
- `convM2TR` decodes request type, auth ids, challenge, host id, uid, and auth domain.

Important details:
- Ticket requests are not encrypted by this conversion routine.
