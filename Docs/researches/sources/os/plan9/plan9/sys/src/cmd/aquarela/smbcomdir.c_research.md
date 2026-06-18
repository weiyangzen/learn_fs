# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdir.c

Server handler for `SMB_COM_CHECK_DIRECTORY`.

Key behavior:
- Requires zero word count and path buffer format `0x04`.
- Resolves tree, stats full path, verifies `DMDIR`, checks read access, and returns ack.

Interactions:
- Uses Plan 9 `dirstat` and `access`.

Notable details:
- Logs stat path through `smblogprintif(1, ...)`, which is unconditional.
