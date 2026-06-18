# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomecho.c

Server handler for `SMB_COM_ECHO`.

Key behavior:
- Reads echo count.
- For each echo index, writes a response header, sequence number, and copied request byte payload.
- Sends each response immediately.
- Returns `Ok` after all echoes or `Die` on send failure.

Interactions:
- Uses `smbresponsesend` and response buffer reset behavior.

Notable details:
- Echo is allowed before session establishment by `aquarela.c`.
