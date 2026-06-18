# File Research: sources/os/linux/linux-stable/fs/smb/common/smb2pdu.h

## Summary
Large shared SMB2/SMB3 protocol schema header. It defines command IDs, dialect IDs, header formats, negotiate contexts, transform/compression headers, tree/session/create/read/write/lock/ioctl/query-info PDUs, lease/oplock data, access masks, file information classes, security info flags, and helper constants.

## Main Content
- SMB2 command constants in host and little endian, plus command count and internal command marker.
- Security/signing/encryption sizes and SMB3 key sizes.
- SMB2/SMB3 headers: standard header, SMB3 request variant, transform/encryption header, compression headers and payload headers.
- Tree connect structures, remoted identity context structures, share types, share flags, and share capabilities.
- Negotiation structures for dialects, preauth integrity, encryption, compression, netname, transport capabilities, RDMA transform capabilities, signing capabilities, and POSIX extension advertisement.
- Session setup, logoff, close, flush, read, write, lock, echo, query-directory, notify, and server-to-client notification PDUs.
- Create/open constants and structures: oplock levels, impersonation, desired access, share access, dispositions, create options, create context tags, create request/response, durable handle contexts, lease contexts, POSIX create context, app instance contexts, and disk ID response.
- IOCTL structures: generic ioctl request/response, copychunk request/response, resume key response, network interface info, socket address formats, validate negotiate info, and integrity constants.
- Query/set info definitions: info types, file information classes, security info flags, query-info request/response, SMB3.1.1 POSIX qinfo, lease/oplock break/ack records, and generic file access masks.

## Integration Notes
This header is consumed by request builders, response parsers, signing/encryption/compression code, filesystem capability probes, server-side copy/clone, lease/oplock handling, multichannel interface discovery, POSIX extension support, and security descriptor paths. It complements `fscc.h`: `smb2pdu.h` covers SMB2 command framing and command-specific payloads, while `fscc.h` covers many file-system-control and info payload layouts.

## Risks
The entire file is wire ABI. Packing, endian annotations, structure sizes, flexible-array offsets, dialect-specific comments, and magic GUID/tag constants must remain exact. Changes can silently break negotiation, preauth hashing, encryption selection, compression, create contexts, durable handles, leases, RDMA/multichannel, query-info parsing, or ACL/security operations.
