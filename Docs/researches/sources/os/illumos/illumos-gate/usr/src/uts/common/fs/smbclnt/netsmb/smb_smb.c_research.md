# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_smb.c

## Purpose
Implements core SMB1 protocol operations used by the illumos SMB client: negotiate, session setup, logoff, tree connect/disconnect, NT create, close, print-job open/close, readx/writex, and echo.

## Key Elements
`smb_smb_negotiate` sends an SMB1 negotiate request with NT LM dialects and optionally the magic SMB2 dialect, initializes header flags, decodes server capabilities, determines whether signing is required/enabled, negotiates Unicode and NT status behavior, requires extended security, returns the server security blob to userland authentication buffers, clamps max mux/VC/transfer values, and handles the SMB1-to-SMB2 negotiate response via `smb2_parse_smb1nego_resp`.

`smb_smb_ssnsetup` sends extended-security `SMB_COM_SESSION_SETUP_ANDX` with the userland-provided security blob, records the SMB UID, maps `MORE_PROCESSING_REQUIRED` to `EINPROGRESS`, and returns the next security blob to userland. `smb_smb_logoff` sends logoff with a short no-reconnect timeout.

`smb_smb_treeconnect` builds a UNC path from server/share names, sends `TREE_CONNECT_ANDX` as a VC-level request, includes the share password and service type, uses no-interrupt receive to avoid leaking TIDs, parses returned type/options, and marks the share connected with current VC generation. `smb_smb_treedisconnect` sends a short no-reconnect tree disconnect and clears the TID.

`smb1_smb_ntcreate` sends `NT_CREATE_ANDX`, transfers a prepared path mbchain into the request, parses the returned FID, create action, timestamps, attributes, allocation size, and EOF size. `smb1_smb_close`, print-job open/close, `smb_smb_readx`, and `smb_smb_writex` implement SMB1 file close, printer file operations, large offset reads, and writes. `smb_smb_echo` is an internal IOD echo request used to probe unresponsive connections.

## Dependencies
Depends on request-layer helpers, SMB1 constants, SMB2 negotiate fallback hooks, string encoding helpers, time conversion helpers, SMB status/error mapping, connection/share/file-handle structures, UIO copy helpers, and transport/reconnect behavior provided by the IOD.

## Behavior/Risks
Negotiation policy is security-sensitive: local signing requirements can abort connections, anonymous sessions disable signing, and extended security is mandatory in this implementation. Tree connect and open operations use no-interrupt receive to avoid server-side resource leaks if a successful response is missed. Transfer size calculations are conservative and tied to legacy SMB1 server behavior. The SMB1-to-SMB2 negotiate path is unusual by design and depends on `smb_rq_parsehdr` returning `EPROTO` only for negotiate.
