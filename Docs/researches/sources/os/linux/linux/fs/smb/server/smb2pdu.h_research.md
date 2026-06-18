# File Research: sources/os/linux/linux/fs/smb/server/smb2pdu.h

Defines ksmbd server-side SMB2/SMB3 protocol constants, wire response structures, query-info payload structures, and command handler prototypes.

Key contents:
- SMB2/SMB3 sizing defaults and limits: credits, I/O sizes, transform/message sizes, durable handle timeout.
- Create-context structures for allocation size, durable handles, POSIX create response, extended attributes, and security descriptors.
- File information and filesystem information response-size constants.
- Packed wire structs for file access, alignment, alternate name, stream, standard, EA, allocation, disposition, mode, compression, attribute/tag, and POSIX directory info.
- Public SMB2/SMB3 lifecycle and command entry points, including negotiate, session setup, tree connect, open, read/write, ioctl, notify, signing, encryption, and credit handling.
- POSIX file type constants used by POSIX extensions.

Dependencies:
- Includes `ntlmssp.h` and `smbacl.h`.
- Uses common SMB2 constants from shared protocol headers via included types such as `smb2_hdr`, `create_context_hdr`, and `smb_ntsd`.

Role in subsystem:
- This is a protocol ABI header for ksmbd SMB2/3 server code. It does not implement behavior; it pins the wire layouts and exported handler surface used by SMB2 PDU processing.
