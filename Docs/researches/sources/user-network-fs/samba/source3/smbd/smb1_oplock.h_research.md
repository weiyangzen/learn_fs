<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_oplock.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_oplock.h

## Purpose
`smb1_oplock.h` declares the SMB1 oplock break message size and helper functions used by the locking/oplock subsystem.

## Important APIs, types, and functions
`SMB1_BREAK_MESSAGE_LENGTH` is defined as `smb_size + 8*2`, matching an SMB1 header plus eight parameter words and no byte data. `new_break_message_smb1(files_struct *fsp, int cmd, char result[SMB1_BREAK_MESSAGE_LENGTH])` formats a caller-provided buffer. `send_break_message_smb1(files_struct *fsp, int level)` formats and sends the break to the SMB1 client.

## Control flow
Locking/oplock code includes this header when it needs to produce an SMB1 oplock break. Callers can either build the message for inspection/testing or send it directly.

## State and persistence behavior
The header is stateless. The implementation reads file and connection state and emits a network message; oplock state transitions occur in the broader locking subsystem.

## Dependencies and integration points
The declarations require `files_struct` and SMB packet size macros from surrounding smbd headers. They integrate SMB1 wire formatting with generic oplock break logic.

## Risks and test signals
The macro length must remain consistent with `new_break_message_smb1()`'s `srv_smb1_set_message(..., 8, 0, ...)` call. Compile and unit tests should catch signature drift; byte-layout tests should catch macro or format mismatches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_oplock.h -->
