<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_lanman.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_lanman.h

## Purpose
`smb1_lanman.h` exposes the SMB1 LANMAN/RAP transaction entry point implemented in `smb1_lanman.c`. It is a narrow header used by the SMB1 transaction handling path to hand IPC transaction payloads to the legacy remote API dispatcher.

## Important APIs, types, and functions
The sole declaration is `api_reply(connection_struct *conn, uint64_t vuid, struct smb_request *req, char *data, char *params, int tdscnt, int tpscnt, int mdrcnt, int mprcnt)`. The arguments carry the active connection, virtual user id, request object, input transaction data/parameter buffers and their counts, and caller-advertised maximum data/parameter response sizes.

## Control flow
Callers include this header when they have already parsed an SMB transaction request as a RAP/IPC operation. They pass the raw transaction sections to `api_reply()`, which owns command id decoding, authorization checks, handler dispatch, reply buffer construction, and transaction reply sending.

## State and persistence behavior
The header stores no state. It exposes an API that can read or mutate backing Samba state through its implementation, including shares, print queues, accounts, passwords, and browse/session data depending on the RAP command id.

## Dependencies and integration points
The declaration depends on `connection_struct` and `struct smb_request` being visible from the including smbd headers. It forms the compile-time contract between generic SMB1 transaction code and the LANMAN remote-admin compatibility module.

## Risks and test signals
The main risk is signature drift: every caller must pass input and maximum lengths in the same units expected by `api_reply()`. Tests that cover SMB1 RAP transaction dispatch also cover this header contract. Build coverage should catch prototype mismatches, while runtime tests should verify that malformed counts are rejected by the implementation rather than trusted by callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_lanman.h -->
