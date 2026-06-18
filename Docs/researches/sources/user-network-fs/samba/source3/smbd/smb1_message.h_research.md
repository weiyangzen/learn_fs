<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_message.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_message.h

## Purpose
`smb1_message.h` declares the SMB1 winpopup messaging command handlers implemented in `smb1_message.c`.

## Important APIs, types, and functions
It exports four request handlers: `reply_sends(struct smb_request *req)`, `reply_sendstrt(struct smb_request *req)`, `reply_sendtxt(struct smb_request *req)`, and `reply_sendend(struct smb_request *req)`. Each handler consumes a parsed SMB1 request and writes its own SMB1 response or error.

## Control flow
The SMB1 command dispatch layer includes this header and calls the appropriate function for the command code. The one-shot handler delivers immediately, while the start/text/end trio coordinates through per-connection SMB1 message state owned by the implementation.

## State and persistence behavior
The header itself is stateless. Its declared functions can create and clear `xconn->smb1.msg_state`, create temporary message files, and run the configured external message command.

## Dependencies and integration points
The only visible dependency is `struct smb_request`. The functions integrate with the SMB1 dispatcher and the connection-level SMB1 state block.

## Risks and test signals
Prototype mismatch is the primary header-level risk. Runtime coverage should include dispatching all four SMB command codes through the normal SMB1 request path and verifying that the implementation emits expected SMB status codes and preserves connection state only between `sendstrt` and `sendend`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_message.h -->
