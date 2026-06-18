# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2pdu.h

## Summary
Defines SMB2/SMB3 PDU-adjacent structures, constants, vector-count limits, create-context payloads, IOCTL payloads, POSIX extension directory payloads, and WSL EA constants used by the SMB2 worker implementation.

## Main Responsibilities
- Define SMB2 transform and RDMA transform header sizes and structures.
- Describe SMB2 symlink and SMB 3.1.1 error-context response payloads, including share-redirect address records.
- Set request/response sizing constants for create and read/write PDUs.
- Define lease-state bits and fixed create-context payload structures for timewarp, query-on-disk-id, and security descriptor create contexts.
- Define FSCTL request/response structures for retrieval pointers, DFS referral request payloads, network resiliency, and compression.
- Define maximum iovec counts for `CREATE`, `IOCTL`, and query-directory request construction.
- Define packed SMB2 file information structures for EA, reparse point, file-id, and file-id extended directory responses.
- Define SMB3 POSIX create response and query-directory entry structures, plus a parsed helper structure for variable-length POSIX entry data.
- Define WSL EA names and expected EA response-size bounds.

## Key Types And Constants
- `SMB2_TRANSFORM_HEADER_SIZE`, `MAX_SMB2_HDR_SIZE`, and `SMB2_READWRITE_PDU_HEADER_SIZE` establish transport/protocol header sizing assumptions.
- `struct smb2_rdma_transform` and `struct smb2_rdma_crypto_transform` describe RDMA transform metadata.
- `struct smb2_symlink_err_rsp`, `struct smb2_error_context_rsp`, and `struct share_redirect_error_context_rsp` model special error response payloads.
- `SMB2_CREATE_IOV_SIZE`, `MAX_SMB2_CREATE_RESPONSE_SIZE`, `SMB2_IOCTL_IOV_SIZE`, and `SMB2_QUERY_DIRECTORY_IOV_SIZE` bound stack iovec arrays used in `smb2pdu.c`.
- `struct crt_twarp_ctxt`, `struct crt_query_id_ctxt`, and `struct crt_sd_ctxt` are create-context wrappers.
- `struct smb2_posix_info` and `struct smb2_posix_info_parsed` support SMB3 POSIX directory parsing.

## Important Behavior
All wire structures are packed and intentionally mirror MS-SMB2/MS-FSCC/SMB3 POSIX extension layouts. Several structures contain flexible array members or comments describing trailing data, so callers must validate offsets and lengths before dereferencing. The create iovec limit is tied directly to the optional context set assembled in `SMB2_open_init()`.

## Cross-File Interactions
`smb2pdu.c` consumes nearly every definition in this header for request construction and response parsing. Directory code and reparse/symlink handling use the file-id, POSIX, and symlink response structures through public helpers declared in `smb2proto.h`.

## Risks
Wire layout drift is the primary risk. Changing packed structures, vector-count limits, alignment assumptions, or WSL/SMB3 POSIX size constants requires coordinated updates to builders and validators in `smb2pdu.c`; otherwise malformed requests, buffer overruns, or rejected server responses can result.
