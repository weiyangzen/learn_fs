# sources/user-network-fs/libsmb2/lib/smb2-signing.h

## Purpose
Declares the SMB2 signing API used by the rest of libsmb2.

## Important APIs, Types, And Functions
The header exposes `smb2_pdu_add_signature(struct smb2_context *, struct smb2_pdu *)` and `smb2_pdu_check_signature(struct smb2_context *, struct smb2_pdu *)`.

## Control Flow
There is no executable control flow. The include guard `_SMB2_SIGNING_H_` protects declarations, and C++ linkage wrappers expose a C ABI.

## State And Persistence
No state is stored in the header. The declared functions operate on SMB2 context and PDU state supplied by callers.

## Dependencies And Integration Points
Includes `slist.h`, `smb2.h`, `libsmb2.h`, `libsmb2-raw.h`, and `libsmb2-private.h`, making it an internal signing interface rather than a small standalone public header.

## Risks
The declared check function currently maps to a stub implementation in `smb2-signing.c`; callers expecting verification through this API would be misled. The broad private includes increase compile coupling.

## Test Signals
Compile C and C++ translation units including this header, ensure prototypes stay synchronized with implementation, and add a test that fails if `smb2_pdu_check_signature` remains a no-op in paths that rely on it.
