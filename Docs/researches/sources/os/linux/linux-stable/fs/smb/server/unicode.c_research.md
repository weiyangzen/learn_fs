# File Research: sources/os/linux/linux-stable/fs/smb/server/unicode.c

## Summary
Implements ksmbd character-set conversion helpers between local NLS strings and SMB UTF-16LE wire strings, including special SMB character remapping and limited surrogate/variation-sequence handling for UTF-8.

## Main Responsibilities
- Convert individual UTF-16 characters to the configured local codepage with optional SMB special-character mapping.
- Compute the output byte length of a UTF-16LE string in a target codepage.
- Convert UTF-16LE strings to local strings with bounds-aware null termination.
- Convert local strings to UTF-16LE using the configured NLS table.
- Duplicate SMB wire strings into allocated local strings.
- Convert local path/name strings to UTF-16LE with optional remapping of `:`, `*`, `?`, `<`, `>`, and `|` to private Unicode values.

## Key Interfaces
`smb_strtoUTF16()`, `smb_strndup_from_utf16()`, and `smbConvertToUTF16()`.

## Important Behavior
UTF-8 receives special handling through `utf8s_to_utf16s()`, `utf16s_to_utf8s()`, and `utf8_to_utf32()` to support non-plane-0 characters better than plain NLS callbacks. Unknown or invalid characters fall back to `?`. Backslash/slash remapping is intentionally not handled because path construction uses separators internally.

## Cross-File Interactions
Used by short-name generation, path/name conversion, directory encoding, and SMB request parsing. The header also declares `ksmbd_extract_sharename()`, implemented outside this file.

## Risks
Conversion functions are length-sensitive and operate on wire-controlled buffers. Off-by-one errors, incorrect surrogate advancement, or mismatched null-termination assumptions can corrupt SMB names or truncate paths.
