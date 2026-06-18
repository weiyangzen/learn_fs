# sources/user-network-fs/samba/source3/smbd/smb1_signing.h

### Purpose
`smb1_signing.h` declares the SMB1 server-signing adapter API used by SMB1 receive/send, negotiation, and session setup code.

### Important APIs, Types, And Functions
It forward-declares `struct smbXsrv_connection` and declares functions to check incoming MACs, calculate outgoing MACs, cancel a response in the signing stream, mark signing as negotiated, query active/negotiated state, activate signing with session key and response blobs, and initialize signing state for a connection.

### Control Flow
The header has no executable logic. The API sequence is: initialize signing during negotiation, update negotiated flags from session setup/client flags, activate after authentication yields a session key, then check/sign packets during I/O.

### State And Persistence Behavior
No state is stored in the header. The implementation owns `conn->smb1.signing_state` and optional anonymous shared memory.

### Dependencies And Integration Points
The declarations depend on Samba `DATA_BLOB`, `NTSTATUS`, `loadparm_context`, and `smbXsrv_connection` types. The API is consumed by SMB1 session setup, SMB1 packet send/receive code, and reply handlers that need to know whether signing disables raw/direct I/O.

### Risks
The API exposes security-sensitive state transitions. Callers must not call activation with the wrong key material or assume `set_signing()` reports hard failure. Query functions should be used consistently before permitting optimizations that bypass normal packet signing.

### Test Signals
Compile coverage plus SMB1 signing negotiation/authentication/integrity tests validate this header. Tests that exercise sendfile/raw I/O decisions indirectly validate consumers of `smb1_srv_is_signing_active()`.
