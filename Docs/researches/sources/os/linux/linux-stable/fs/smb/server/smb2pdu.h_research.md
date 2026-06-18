# File Research: sources/os/linux/linux-stable/fs/smb/server/smb2pdu.h

## Summary
Defines KSMBD SMB2/SMB3 PDU constants, wire-adjacent structures, file/filesystem information sizes, create-context payloads, POSIX extension structures, and the public server-side SMB2 handler prototypes implemented by `smb2pdu.c`.

## Main Responsibilities
- Define SMB2 create actions, credit limits, maximum header and I/O sizing defaults.
- Store SMB 3.1.1 preauth integrity state and negotiate-context offsets.
- Define session state bits and timeout constants.
- Define create-context payload wrappers for allocation size, durable responses, POSIX responses, EA buffers, and security descriptor buffers.
- Define IOCTL response structures for socket addresses, file object ids, sparse flag setting, and network interface responses.
- Define file and filesystem information class response-size constants used by query/set info handlers.
- Define packed SMB2 file information payloads for access, alignment, alternate name, streams, standard info, EA info, allocation, disposition, position, mode, compression, attribute tags, EA entries, and POSIX directory/query data.
- Declare the KSMBD SMB2 command handlers and signing/encryption helpers.
- Define POSIX file type constants used in SMB3 POSIX mode encoding.

## Key Types And Constants
- `struct preauth_integrity_info` stores the negotiated preauth hash id and hash value.
- `OFFSET_OF_NEG_CONTEXT` captures the negotiate-context offset difference between Kerberos-enabled and non-Kerberos builds.
- `SMB2_SESSION_EXPIRED`, `SMB2_SESSION_IN_PROGRESS`, and `SMB2_SESSION_VALID` describe session lifecycle state.
- `struct create_alloc_size_req`, `struct create_durable_rsp`, `struct create_posix_rsp`, `struct create_ea_buf_req`, and `struct create_sd_buf_req` mirror create-context payloads consumed by `smb2_open()`.
- `struct smb2_ea_info_req` and `struct smb2_ea_info` define EA query/set payload layout.
- `struct smb2_posix_info` defines SMB3 POSIX directory information with embedded SID and variable name data.
- Handler declarations include `smb2_handle_negotiate()`, `smb2_sess_setup()`, `smb2_tree_connect()`, `smb2_open()`, `smb2_query_info()`, `smb2_query_dir()`, `smb2_set_info()`, `smb2_read()`, `smb2_write()`, `smb2_lock()`, `smb2_ioctl()`, and `smb2_oplock_break()`.

## Important Behavior
The structures are packed wire-format definitions, so callers must validate offsets, buffer lengths, and variable tails before use. The size constants in this header are directly coupled to response encoding in `smb2pdu.c`; changing them affects buffer sizing, info-class validation, and iovec pinning.

## Cross-File Interactions
`smb2pdu.c` is the primary consumer and implementer of the declarations here. Other KSMBD protocol, transport, connection, and dispatch code uses these prototypes to initialize dialect behavior, validate SMB2 messages, route command handlers, and apply signing/encryption processing.

## Risks
The main risk is wire-layout drift. Any change to packed structures, info-class sizes, negotiate offsets, POSIX mode constants, or handler prototypes must be synchronized with request validation and response construction in `smb2pdu.c`; otherwise clients can receive malformed PDUs or server-side bounds checks can become incorrect.
