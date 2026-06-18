# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbconnect.c

Client-side SMB connection, negotiation, authentication, tree connect, and transaction transport adapters.

Key functions:
- `smbconnect` resolves/dials NetBIOS session service, sends `SMB_COM_NEGOTIATE`, parses peer info/challenge/domain, sends `SMB_COM_SESSION_SETUP_ANDX` with MS-CHAP response chained to IPC tree connect, optionally connects a requested disk share, and returns `SmbClient`.
- `smbclientfree` frees client peer info, buffer, and object.
- `smbtransactionclientsend` and `smbtransactionclientreceive` adapt NBSS transport for transaction execution.

Interactions:
- Uses `nbssconnect`, `smbbuffer`, `smbcommon`, auth APIs, and transaction client code.

Notable details:
- Rejects servers requiring extended security.
- Hardcodes auth server string `"cher"` in `auth_respond`.
