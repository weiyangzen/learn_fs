# sources/user-network-fs/libsmb2/lib/smb3-seal.h

## Purpose
Declares the internal SMB3 sealing encrypt/decrypt functions.

## Important APIs, Types, And Functions
The header exports `smb3_encrypt_pdu(struct smb2_context *, struct smb2_pdu *)` and `smb3_decrypt_pdu(struct smb2_context *)`.

## Control Flow
There is no executable logic. Include guards and C++ extern wrappers provide safe inclusion from C and C++ code.

## State And Persistence
The header stores no state. The declared functions mutate SMB2 context and PDU encryption buffers in their implementation.

## Dependencies And Integration Points
Unlike `smb2-signing.h`, this header forward-uses `struct smb2_context` and `struct smb2_pdu` without including their definitions directly, relying on includers such as `socket.c` or `smb3-seal.c` to include SMB2 headers first.

## Risks
Because it lacks explicit forward declarations, strict compilers may warn if included before definitions in some translation units. Prototype drift would break socket integration.

## Test Signals
Compile include-order tests, C++ linkage tests, and integration tests ensuring socket encryption paths call these prototypes with the expected context/PDU types.
