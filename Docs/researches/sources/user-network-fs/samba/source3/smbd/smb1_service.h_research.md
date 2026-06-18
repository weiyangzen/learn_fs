# sources/user-network-fs/samba/source3/smbd/smb1_service.h

### Purpose
`smb1_service.h` exposes the SMB1 tree-connect service opener `make_connection()` to the SMB1 reply layer.

### Important APIs, Types, And Functions
The single declaration is `connection_struct *make_connection(struct smb_request *req, NTTIME now, const char *service_in, const char *pdev, uint64_t vuid, NTSTATUS *status)`. It returns a live `connection_struct` on success and returns NULL with `*status` set on failure.

### Control Flow
The header has no executable logic. Its API shape shows that callers provide request/session context, current time, service and device strings from the wire, VUID, and a status out-parameter.

### State And Persistence Behavior
No state is stored here. The implementation creates in-memory tcon/connection state and may trigger common share setup side effects.

### Dependencies And Integration Points
The declaration depends on Samba request, time, status, and connection types. It is consumed by `reply_tcon()` and `reply_tcon_and_X()` in the SMB1 reply implementation.

### Risks
The function leaves the process as root according to implementation comments, so callers must not assume user impersonation on return. API changes would affect SMB1 tree-connect handlers directly.

### Test Signals
Compile coverage plus SMB1 tree-connect integration tests validate this header's contract.
