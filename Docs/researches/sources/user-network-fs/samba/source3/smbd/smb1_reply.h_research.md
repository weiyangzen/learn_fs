# sources/user-network-fs/samba/source3/smbd/smb1_reply.h

### Purpose
`smb1_reply.h` declares the SMB1 command handlers and small exported helpers implemented primarily in `smb1_reply.c`. It is the dispatch-facing interface for legacy SMB1 replies.

### Important APIs, Types, And Functions
The header exports `reply_*` handlers for tree connect, IOCTL, path/attribute operations, legacy searches, opens, session logoff, creates, deletes, reads, writes, seeks, flush, close, locking, echo, printing, directory management, rename/copy, obsolete multiplex commands, extended attributes, and find close commands. It also exports `setup_readX_header()`, `error_to_writebrawerr()`, `is_valid_writeX_buffer()`, `get_lock_pid()`, and `get_lock_count()`. All handlers take `struct smb_request *`; lock parsers operate on wire data and a large-file-format flag.

### Control Flow
The header has no runtime control flow. Its structure mirrors the SMB1 command dispatch surface and groups helpers near the commands that need them.

### State And Persistence Behavior
No state is stored in the header. The declarations imply mutations performed by implementation files: request output buffers, file/session/tree state, VFS state, locks, and printer state.

### Dependencies And Integration Points
Consumers must include definitions for `struct smb_request`, `struct smbXsrv_connection`, `connection_struct`, `DATA_BLOB`, and Samba scalar types. The file integrates with SMB1 dispatch tables and with recvfile/signing logic through `is_valid_writeX_buffer()`.

### Risks
Because this is a broad exported surface, prototype drift can break SMB1 dispatch or helper callers. Exporting raw helper names without namespacing beyond SMB1 also means new helper additions should avoid conflicts.

### Test Signals
Compile/link coverage is the main direct signal. Behavioral coverage comes from command-dispatch tests that ensure every declared handler still matches the implementation signature and is callable by the SMB1 switch layer.
