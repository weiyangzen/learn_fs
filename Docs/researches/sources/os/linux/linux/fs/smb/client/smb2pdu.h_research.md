# File Research: sources/os/linux/linux/fs/smb/client/smb2pdu.h

## Purpose

`smb2pdu.h` defines SMB2/SMB3 PDU-adjacent constants and wire structures used by the CIFS SMB2 client implementation. It supplements the broader SMB2 structure definitions with create-context, RDMA transform, ioctl/fsctl, POSIX extension, WSL xattr, symlink error, and share redirect layouts.

## Main Contents

- Header and transform size constants: `SMB2_TRANSFORM_HEADER_SIZE`, `MAX_SMB2_HDR_SIZE`, and `SMB2_READWRITE_PDU_HEADER_SIZE`.
- SMB Direct/RDMA transform structures and transform type constants.
- Symlink and SMB3.1.1 error context response layouts.
- Share redirect error context structures including target IP address records.
- Create request iovec sizing and max create response sizing.
- Lease caching flags.
- Create context structures for timewarp, query-on-disk-id, and security descriptor contexts.
- FSCTL request/response structs for retrieval pointers, DFS referral, network resiliency, and compression.
- SMB2 query info structures for EA, reparse-point, file-id, and file-id extended directory information.
- POSIX create response and SMB3 POSIX directory info structures, plus parsed helper representation.
- WSL EA/xattr names and size constants.

## Integration

- Included by `smb2pdu.c` and other SMB2 client files that need these wire layouts.
- Depends on `cifsacl.h` for SID/security-descriptor-related types.
- Exposes `smb2_padding[7]`, used by request free paths to avoid freeing static padding as dynamic iovec memory.
- The `SMB2_CREATE_IOV_SIZE`, `SMB2_IOCTL_IOV_SIZE`, and `SMB2_QUERY_DIRECTORY_IOV_SIZE` constants directly constrain the request-building code in `smb2pdu.c`.

## Risk Notes

- All wire structs are packed and endian-sensitive. Field additions or reordering would break protocol layout.
- Flexible arrays and variable-length trailing fields require callers to validate lengths before access.
- The create iovec size must remain in sync with every optional context that `SMB2_open_init()` can append.
