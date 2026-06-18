# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smblisten.c

Direct CIFS TCP listener on port/service `cifs`.

Key functions:
- `smblistencifs` announces `tcp!*!cifs`, records the accept callback, and starts listener process.
- `tcplistener` accepts TCP connections and creates sessions.
- `createsession` allocates a direct `SmbCifsSession`, calls accept callback, starts `tcpreader`, and links session.
- `tcpreader` reads RFC 1002-style 4-byte length headers plus SMB payload and calls the session write callback.
- `deletesession` closes fd, unlinks, and frees session.

Interactions:
- Used by `aquarela.c` direct SMB server mode.

Notable details:
- Unlike `nbss.c`, this path skips NetBIOS session-request negotiation and treats connections as already established at the transport framing level.
