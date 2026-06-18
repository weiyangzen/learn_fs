<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_nttrans.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_nttrans.h

## Purpose
`smb1_nttrans.h` declares the SMB1 NT create and NT transaction request handlers implemented in `smb1_nttrans.c`.

## Important APIs, types, and functions
The header exports `reply_ntcreate_and_X(struct smb_request *req)`, `reply_ntcancel(struct smb_request *req)`, `reply_ntrename(struct smb_request *req)`, `reply_nttrans(struct smb_request *req)`, and `reply_nttranss(struct smb_request *req)`. These correspond to SMB1 NT create-and-X, cancel, NT rename, primary NT transaction, and secondary NT transaction commands.

## Control flow
The SMB1 dispatcher calls these functions based on command code. The primary/secondary NT transaction pair coordinates through pending transaction state in the implementation; callers do not manage assembly directly. Each function owns response emission or asynchronous deferral.

## State and persistence behavior
The header is stateless. The declared implementation can create/open files and pipes, queue transaction fragments, queue notify requests, cancel pending work, rename/copy/hardlink paths, alter security descriptors, perform FSCTLs, and optionally query/set quotas.

## Dependencies and integration points
The visible dependency is `struct smb_request`. The declarations integrate the SMB1 command dispatch layer with VFS, notify, security, pipe, and transaction subsystems through the implementation.

## Risks and test signals
Header-level risk is keeping dispatcher signatures synchronized. End-to-end SMB1 tests should cover each declared command through normal dispatch so command-code binding, request lifetime, transaction state ownership, and response behavior are verified together.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_nttrans.h -->
