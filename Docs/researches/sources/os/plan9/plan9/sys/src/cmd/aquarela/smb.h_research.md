# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smb.h

Defines SMB wire header and protocol constants.

Major contents:
- `SmbRawHeader` matching SMB protocol header layout.
- Header flag and `flags2` capability constants.
- SMB command opcode enum.
- DOS/server/hardware/error class and error code constants.
- Capability flags.
- RAP procedure ids and server/share type constants.
- Transaction2 opcodes and find/query/set information levels.
- DOS attribute constants.
- Open mode/share mode, create disposition, desired access, share access, and create option constants.

Interactions:
- Used throughout command handlers and client/server packet construction.

Notable details:
- Covers classic SMB/CIFS era commands with many unimplemented op table entries elsewhere.
