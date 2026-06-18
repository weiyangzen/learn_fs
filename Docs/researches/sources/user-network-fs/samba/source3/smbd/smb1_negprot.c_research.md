<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_negprot.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_negprot.c

## Purpose
`smb1_negprot.c` implements the SMB1 `SMB_COM_NEGOTIATE` reply path. It parses the client's dialect list, infers remote client architecture, applies configured min/max server protocol constraints, selects the best supported dialect, initializes per-connection protocol tables, advertises capabilities/security/signing settings, and can hand off to SMB2 negotiation when the client offers SMB2 dialects.

## Important APIs, types, and functions
`reply_negprot(struct smb_request *req)` is the exported request handler. `get_challenge()` creates or refreshes `xconn->smb1.negprot.auth_context` via `make_auth4_context()` and fills an 8-byte NTLM challenge. `reply_lanman1()` and `reply_lanman2()` build downlevel LANMAN negotiate responses with security mode, max buffer, max mux, raw-mode flags, PID, server time, timezone, and optional challenge. `reply_nt1()` builds the NT1 response, including extended security/SPNEGO, Unicode, UNIX extensions, large file/read/write, DFS, NT status, raw mode, signing, server time, capabilities, challenge or SPNEGO blob, workgroup, and NetBIOS name.

The `supported_protocols[]` table lists dialect strings in preference order, from SMB2 wildcard and SMB2.002 down through NT1 and LANMAN variants, with a reply function and protocol level. Architecture bitmasks (`PROT_*`, `ARCH_*`) encode common dialect-list fingerprints for Windows, OS/2, Samba, CIFSFS, Vista, and OSX detection.

## Control flow
`reply_negprot()` rejects multiple negotiate attempts on the same SMB1 connection, empty dialect buffers, and non-null-terminated dialect lists. It walks `req->buf` from byte 1, converting each dialect to a talloced ASCII string and advancing by `strlen(p) + 2` because each dialect entry includes a buffer-format byte plus a NUL-terminated string. It ORs recognized dialect names into a protocol bitmask, special-casing `Samba` and `POSIX 2`, then maps exact bitmask combinations to `set_remote_arch()`.

The handler reloads services after architecture detection, clamps configured max/min protocol values above SMB2_10 down to the SMB2 wildcard negotiation level, and scans `supported_protocols[]` in preferred order. A dialect is selectable only if its protocol level lies within configured min/max and appears in the client list. If none match, it sends a one-word negotiate response with dialect index `0xffff` and exits the server cleanly.

For a selected dialect, it sets the remote protocol short name, reloads services again, calls the selected reply builder, marks `xconn->smb1.negprot.done`, and enforces mandatory signing for downlevel protocols by terminating the connection if signing is required but the chosen level is below NT1. If async SMB echo handling is enabled and the chosen level is below SMB2.002, it forks the echo handler.

## State and persistence behavior
Negotiation mutates per-connection state: `xconn->smb1.negprot.done`, `encrypted_passwords`, `auth_context`, max receive/session table initialization through `smbXsrv_connection_init_tables()`, common flags2, signing behavior, selected remote architecture/protocol globals, and potentially echo-handler process state. It also triggers service reloads because architecture/protocol choices can affect configuration substitutions.

## Dependencies and integration points
The module depends on authentication (`make_auth4_context`, NTLM challenge generation, SPNEGO), signing helpers, SMB1/SMB2 protocol reply builders (`reply_smb2002`, `reply_smb20ff`), loadparm settings (`server min/max protocol`, encrypted passwords, raw I/O, Unicode, UNIX extensions, DFS, NT status, large read/write, signing), profile macros, service reload logic, and remote architecture/protocol tracking. It sits at the front of all SMB1 session setup because later commands depend on the negotiated protocol tables and capabilities.

## Risks and edge cases
Dialect parsing is security-sensitive because the input is a packed list of variable strings. The code checks final NUL termination and allocation failures, but relies on the SMB request buffer helpers and dialect entry structure. Multiple negotiation attempts intentionally terminate the server connection. No-protocol selection sends the MS-CIFS-required `0xffff` index before clean exit.

Compatibility risks are high: client architecture inference depends on exact dialect-list bitmasks and affects service reload behavior. Capability advertising must stay consistent with configuration and signing: raw mode is disabled when signing is desired, extended security is only advertised when encrypted passwords and client flags allow it, and mandatory signing rejects LANMAN. SMB2 handoff depends on treating all protocols above SMB2_10 as `SMB 2.???` at the SMB1 negotiate stage.

## Test signals
Tests should exercise dialect lists for NT1, LANMAN1/2, Samba, CIFSFS-only, Vista-style SMB2 wildcard, OSX SMB2.002/wildcard, unsupported dialects, non-NUL-terminated buffers, empty buffers, repeated negotiate, configured min/max protocol boundaries, mandatory signing with downlevel dialects, raw-mode suppression under signing, extended-security SPNEGO vs challenge responses, and async echo handler setup. Wire-level assertions should verify dialect index, security word bits, capabilities, challenge/SPNEGO payload, time fields, and `0xffff` no-protocol behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_negprot.c -->
