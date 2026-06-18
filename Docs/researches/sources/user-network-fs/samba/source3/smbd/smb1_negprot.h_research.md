<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_negprot.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_negprot.h

## Purpose
`smb1_negprot.h` declares the SMB1 negotiate-protocol request handler.

## Important APIs, types, and functions
It exports `reply_negprot(struct smb_request *req)`, the handler for SMB1 `SMB_COM_NEGOTIATE`. The function consumes the dialect list in the request and emits the selected dialect response or an error/connection termination.

## Control flow
The SMB1 dispatcher calls `reply_negprot()` before normal SMB1 session setup and tree operations. Once it completes successfully, the connection has protocol tables, security mode, capabilities, and remote architecture/protocol state initialized.

## State and persistence behavior
The header has no state. The implementation behind the declaration mutates `xconn->smb1.negprot`, signing state, auth challenge context, selected protocol metadata, and possibly echo-handler state.

## Dependencies and integration points
The visible dependency is `struct smb_request`. The declared function integrates with the SMB1 command dispatcher and indirectly with SMB2 negotiation when SMB2 dialects are selected from an SMB1 negotiate frame.

## Risks and test signals
Header-level risk is limited to keeping the request-handler signature consistent with the dispatch table. Functional tests should enter through the SMB1 negotiate command rather than calling internals so the declaration, dispatcher binding, and implementation side effects are all covered.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_negprot.h -->
