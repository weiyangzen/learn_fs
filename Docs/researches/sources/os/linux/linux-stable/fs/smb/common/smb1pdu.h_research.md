# File Research: sources/os/linux/linux-stable/fs/smb/common/smb1pdu.h

## Summary
Defines common SMB1 protocol header structures and the SMB1 negotiate request layout.

## Main Content
- `SMB1_PROTO_NUMBER`: little-endian protocol marker for SMB1.
- `struct smb_hdr`: packed SMB1 header with protocol bytes, command, DOS/CIFS status union, flags, signature/sequence union, TID/PID/UID/MID, and word count.
- `SMB_NEGOTIATE_REQ`: negotiate request containing `struct smb_hdr`, byte count, and variable dialect array.

## Integration Notes
This shared header supports SMB1/CIFS negotiation and common header parsing/building in client/server code. It intentionally mirrors MS-CIFS/MS-SMB wire layout and uses packed fields plus endian-specific types.

## Risks
The header is protocol ABI. Field type, packing, and endian mistakes would corrupt SMB1 parsing or signing. SMB1 is legacy and security-sensitive, so this header should remain narrowly scoped to compatibility paths.
