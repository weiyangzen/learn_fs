# File Research: sources/os/linux/linux/fs/smb/common/smb1pdu.h

## Scope
Read completely: 56 lines. This header defines minimal shared SMB1 PDU structures.

## Purpose
`smb1pdu.h` provides the SMB1 protocol magic value and the common SMB1 header layout, plus the negotiate request wrapper.

## Main Definitions
- `SMB1_PROTO_NUMBER`: little-endian protocol id `0x424d53ff`.
- `struct smb_hdr`: packed SMB1 header matching MS-CIFS/MS-SMB.
- `SMB_NEGOTIATE_REQ`: negotiate request with an SMB header, byte count, and variable dialect array.

## SMB1 Header Fields
`struct smb_hdr` includes:
- protocol bytes.
- command.
- status union for DOS error or CIFS/NT error.
- flags and `Flags2`.
- PID high.
- signature/sequence union.
- TID, PID, UID, MID.
- word count.

## Integration Points
Used by common SMB code and compatibility paths that need SMB1 header parsing or negotiation structure definitions.

## Notable Behaviors
- The structure is packed to match wire layout.
- Some fields are endian-annotated, while opaque or historical fields remain plain-width integers.
- Only the negotiate request is defined here; broader SMB1 command definitions live elsewhere in the client tree.

## Research Takeaways
`smb1pdu.h` is a small shared definition header for legacy SMB1 framing. It exists so common SMB code can identify and parse the basic SMB1 wire header without depending on the full client SMB1 PDU header.
