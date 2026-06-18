# File Research: sources/os/linux/linux/fs/smb/common/smb2pdu.h

## Scope
Read completely: 1,784 lines. This header defines shared SMB2/SMB3 protocol command constants, flags, packed wire PDUs, negotiate contexts, create contexts, FSCTL ioctl payloads, query/set info classes, lease/oplock structures, and access-right constants.

## Purpose
`smb2pdu.h` is the core common SMB2/3 wire-format vocabulary. It is shared by client and server code so both sides build and parse the same packed protocol structures.

## Command And Size Constants
Defines host-endian and little-endian command ids for:
- negotiate, session setup, logoff, tree connect/disconnect, create, close, flush, read, write, lock, ioctl, cancel, echo, query directory, change notify, query info, set info, oplock break, and server-to-client notification.

Also defines:
- `NUMBER_OF_SMB2_COMMANDS`
- session key and signature sizes.
- AES-GCM/CCM key sizes.
- SMB3 encryption/decryption and signing key sizes.
- SMB2 max buffer size.
- default I/O sizes.
- SMB2 header size and protocol numbers for normal, encrypted transform, and compression transform frames.

## Header And Transform Structures
Defines:
- `struct smb2_hdr`
- `struct smb3_hdr_req`
- `struct smb2_pdu`
- `struct smb2_err_rsp`
- `struct smb2_transform_hdr`
- `struct smb2_compression_hdr`
- `struct smb2_compression_payload_hdr`
- `struct smb2_compression_pattern_v1`

These structures model normal SMB2 frames, SMB3 request headers with channel sequence fields, encrypted transform frames, and compressed frames.

## Tree Connect And Remoted Identity
Defines tree connect contexts:
- generic `tree_connect_contexts`.
- remoted identity blob and SID/group/privilege arrays.
- `remoted_identity_tcon_context`.
- `smb2_tree_connect_req_extension`.

Also defines tree connect request/response structures, tree disconnect request/response structures, share types, share flags, and share capabilities such as DFS, continuously available, scaleout, cluster, asymmetric, redirect-to-owner, compression, and isolated transport.

## Negotiation
Defines:
- security mode flags.
- global capabilities including DFS, leasing, large MTU, multichannel, persistent handles, directory leasing, encryption, and notifications.
- dialect ids from SMB2.0 through SMB3.1.1.
- SMB3.1.1 salt/preauth constants.
- negotiate context ids for preauth integrity, encryption, compression, netname, transport, RDMA transform, signing, and POSIX extension availability.

Packed negotiate context structures include:
- `smb2_neg_context`
- `smb2_preauth_neg_context`
- `smb2_encryption_neg_context`
- `smb2_compression_capabilities_context`
- `smb2_netname_neg_context`
- `smb2_transport_capabilities_context`
- `smb2_rdma_transform_capabilities_context`
- `smb2_signing_capabilities`
- `smb2_posix_neg_context`
- `smb2_negotiate_req`
- `smb2_negotiate_rsp`

## Session, Logoff, Close, Read, Write, Flush, Lock, Echo
Defines request/response structures and flags for:
- `smb2_sess_setup_req` / `rsp`, including binding and encryption flags.
- logoff.
- close with post-query attributes and close response metadata.
- read requests/responses, unbuffered/compressed read flags, channel flags, and RDMA transform response flags.
- write requests/responses with write-through and unbuffered flags.
- flush.
- byte-range lock request/response and lock element flags.
- echo.

## Directory, Notify, Device Flags, Set Info
Defines:
- query-directory flags and request/response structures.
- device type and device characteristic constants.
- set-info request/response and `SMB2_SET_INFO_IOV_SIZE`.
- change-notify flags, completion filters, request/response structures.
- server-to-client notification structure and session-closed notification type.

## Create/Open And Create Contexts
Defines:
- oplock levels, including internal `SMB2_OPLOCK_LEVEL_NOCHANGE`.
- impersonation levels.
- little-endian desired access, share access, create disposition, and create options flags.
- create context names such as extended attributes, security descriptor, durable handle, maximal access, timewarp, on-disk id, lease, POSIX, app instance ids, SVHDX, and AAPL.
- create request and response structures.
- POSIX create context.
- durable handle v1/v2 request/reconnect/response contexts.
- maximal access request/response.
- lease v1/v2 contexts.
- disk id response.
- app instance id/version contexts.

## IOCTL And FSCTL Payloads
Defines:
- `smb2_ioctl_req` and `smb2_ioctl_rsp`.
- copychunk request/response payloads.
- resume key response.
- SMB socket address structures for IPv4 and IPv6.
- network interface info response and RSS/RDMA capability constants.
- integrity checksum choices and flags.
- validate negotiate request/response.

These definitions back SMB3 copy offload, multichannel interface discovery, integrity streams, and validate-negotiate behavior.

## Query Info, POSIX Info, Oplock/Lease Breaks
Defines:
- SMB2 info type constants for file, filesystem, security, quota.
- file information class numbers, including query-directory-compatible values and SMB3 POSIX info.
- security info flags such as owner, group, DACL, SACL, label, scope, backup, and protected/unprotected DACL/SACL.
- EA scan flags.
- `smb2_query_info_req` / `rsp`.
- `smb311_posix_qinfo`.
- oplock break, lease break, and lease ack structures.
- structure size constants for SMB2.0 and SMB2.1 oplock break acknowledgements.

## Access Rights
The final section defines non-endian access-right constants:
- file read/write/append/list/traverse/EA/attribute/delete rights.
- `DELETE`, `READ_CONTROL`, `WRITE_DAC`, `WRITE_OWNER`, `SYNCHRONIZE`.
- `SYSTEM_SECURITY`, `MAXIMUM_ALLOWED`, and generic read/write/execute/all.
- helper masks such as `FILE_READ_RIGHTS`, `FILE_WRITE_RIGHTS`, `FILE_EXEC_RIGHTS`, `SET_FILE_EXEC_RIGHTS`, and `SET_MINIMUM_RIGHTS`.

These are used by ACL, create/open, chmod-like behavior, and security descriptor logic.

## Integration Points
This header is central to:
- SMB2/3 client PDU builders/parsers in `fs/smb/client`.
- SMB server code that parses or emits SMB2/3 frames.
- common FSCC and ACL code through shared security/access constants.
- transport and stats code through command ids and response sizes.
- encryption, compression, multichannel, leasing, durable handles, copy offload, and POSIX extension paths.

## Notable Behaviors
- Names intentionally follow Microsoft protocol field casing rather than normal kernel style.
- All wire structures are packed.
- Many fields use explicit little-endian types; FIDs are documented as opaque endianness in several structures.
- Some contexts contain flexible arrays and protocol-required padding comments.
- The header mixes base SMB2, SMB3, SMB3.0.2, SMB3.1.1, POSIX extension, RDMA, compression, signing, encryption, and copychunk definitions.

## Risks And Review Focus
- Wire layout changes are high risk; structure sizes and offsets must match MS-SMB2.
- Flexible-array payloads require strict caller-side bounds validation.
- Dialect-specific fields must be zero or ignored correctly for older dialects.
- Security and access-right constants are used in ACL-sensitive code; mismatches affect authorization behavior.
- Some comments note expansion or padding concerns, such as validate-negotiate dialect count and compression context padding.

## Research Takeaways
`smb2pdu.h` is the shared SMB2/3 protocol contract for this tree. It is not executable logic, but it defines nearly every object that SMB client/server code sends, receives, signs, encrypts, validates, and exposes to higher filesystem logic.
