# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrap2.c

Implements SMB RAP over `/PIPE/LANMAN` server-side procedures.

Key components:
- `InfoMethod` abstracts size, fixed-structure serialization, string serialization, and enumeration.
- Server info helpers serialize `SmbServerInfo` levels 0/1.
- Share info helpers serialize `SmbService` levels 0/1/2.
- `thingfill` and `onethingfill` fill RAP output parameter/data buffers and report `MORE_DATA` when truncated.
- RAP procedures: `NetShareEnum`, `NetServerEnum2`, `NetShareGetInfo`, `NetServerGetInfo`, and `NetWkstaGetInfo`.
- `smbrap2` parses RAP procedure number, parameter descriptor, and data descriptor, then dispatches through `raptable`.

Interactions:
- Called by `smbcomtransaction` for `/PIPE/LANMAN`.
- Uses global services and server identity from `smbglobals`/`smbservice`.

Notable details:
- `netservergetinfo` appears to pass `&shareinfo` while using `&smbglobals.serverinfo`, likely intended to use `serverinfo`.
