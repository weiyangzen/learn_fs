# sources/user-network-fs/samba/source4/smb_server/smb2/negprot.c

## Purpose
This file handles SMB2 negotiation and the SMB1-to-SMB2 negotiation bridge for dialect `SMB 2.002`. It selects the SMB2 dialect, computes signing mode and transfer limits, initializes the first SPNEGO security blob, and serializes the negotiate response.

## Important APIs, Types, And Functions
The public entry points are `smb2srv_negprot_recv` and `smb2srv_reply_smb_negprot`. Internal functions include `smb2srv_negprot_secblob`, `smb2srv_negprot_backend`, and `smb2srv_negprot_send`. The implementation uses `struct smb2_negprot`, GENSEC/SPNEGO APIs, server credentials, loadparm signing settings, GUID and NTTIME helpers, and `req->smb_conn->negotiate`.

## Control Flow
`smb2srv_negprot_recv` validates the body, decodes dialect count, client GUID, start time, and dialect list, then calls the backend and sends the reply unless suppressed. The backend only accepts `SMB2_DIALECT_REVISION_202`, sets `PROTOCOL_SMB2_02`, derives signing requirements from `server signing` and server role, sets max transact/read/write sizes from smb2 parameters, and obtains a SPNEGO blob. `smb2srv_negprot_secblob` initializes server credentials, starts a server GENSEC context for `cifs`, selects SPNEGO, and asks for the initial token. `smb2srv_reply_smb_negprot` fabricates an SMB2 negprot request from an SMB1 dialect negotiation path.

## State And Persistence
Negotiation persists on the connection: selected protocol, server credentials, max sizes, zone/time-related values initialized elsewhere, and `smb2_signing_required` when signing is mandatory. No disk state is changed.

## Dependencies And Integration Points
This module integrates authentication (`gensec`, credentials), loadparm policy, SMB1 negotiation fallback, and SMB2 request framing. It is reached from `receive.c` for native SMB2 and from the SMB1 negotiate code through `smb2srv_reply_smb_negprot`.

## Risks And Test Signals
Risks include support for only SMB2.002, no real boot-time value, fallback anonymous credentials for standalone/spoolss tests, hard connection termination on GENSEC startup failures, and signing policy regressions for AD DC roles. Tests should cover no dialects, unsupported dialects, SMB2.002, SMB1 negotiate upgrade, signing off/desired/required/default on DC and non-DC roles, max-size loadparm overrides, and SPNEGO token creation failure.
