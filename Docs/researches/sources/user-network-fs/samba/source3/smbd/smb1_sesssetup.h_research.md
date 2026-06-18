# sources/user-network-fs/samba/source3/smbd/smb1_sesssetup.h

### Purpose
`smb1_sesssetup.h` exposes the SMB1 session setup command handler.

### Important APIs, Types, And Functions
The single declaration is `void reply_sesssetup_and_X(struct smb_request *req)`. It is the dispatch entry point for SMB1 `SMBsesssetupX`.

### Control Flow
The header has no executable control flow. The implementation decides between SPNEGO and legacy authentication based on word count, flags, negotiated protocol, and connection state.

### State And Persistence Behavior
No state is stored in the header. The implementation creates and updates authenticated SMB1 session state, signing keys, client capability state, and homes share registration.

### Dependencies And Integration Points
The declaration depends on `struct smb_request` and is consumed by SMB1 command dispatch. It connects authentication to later tree-connect and file-access paths because `req->session`, VUID, signing, and `session->homes_snum` are established by the implementation.

### Risks
Any signature change would affect the SMB1 dispatch table. The handler must remain callable with `req->conn == NULL`, as session setup occurs before tree connect.

### Test Signals
Compile coverage and SMB1 authentication integration tests validate this header's contract.
