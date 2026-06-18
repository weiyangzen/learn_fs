# File Research: sources/os/linux/linux-stable/fs/smb/server/unicode.h

## Summary
Declares ksmbd Unicode/NLS conversion helpers and includes kernel NLS/Unicode support headers.

## Main Responsibilities
- Declare local-to-UTF16 and UTF16-to-local conversion functions.
- Declare `ksmbd_extract_sharename()` for extracting share names from tree names.
- Include UCS-2 utility support used by SMB Unicode handling.

## Cross-File Interactions
Consumed by SMB path parsing, name encoding, short-name generation, and tree/share-name handling.

## Risks
The declared functions are used on SMB wire strings, so their callers depend on strict buffer length and null-termination semantics.
