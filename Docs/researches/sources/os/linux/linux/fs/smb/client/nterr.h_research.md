# File Research: sources/os/linux/linux/fs/smb/client/nterr.h

## Purpose
Defines NTSTATUS constants and the `ntstatus_to_dos_err` mapping record used by SMB error translation code.

## Main Contents
- `struct ntstatus_to_dos_err` with DOS class, DOS code, NTSTATUS value, and string name.
- Win32-style error constants used in SMB status handling.
- A large list of `NT_STATUS_*` definitions covering success, pending, informational statuses, filesystem errors, object/path errors, network errors, auth/account errors, pipe errors, DFS errors, encryption errors, reparse statuses, and SMB3 preauth negotiation errors.
- Comments beside most constants encode the DOS class/code mapping used to generate SMB1 mapping tables.

## Integration Points
Included by SMB error mapping and helper code such as `netmisc.c`, `misc.c`, and SMB1/SMB2 error translation units.

## Notable Behaviors
This is a schema/header file rather than executable logic. It centralizes numeric NTSTATUS definitions so protocol parsers and error mappers can use symbolic names consistently.

## Risks And Review Focus
- Numeric constants must match Windows/SMB protocol definitions.
- Mapping comments are data for generated tables, so comment format changes can affect generation.
- Adding new statuses should preserve endian and integer-width expectations at use sites.
