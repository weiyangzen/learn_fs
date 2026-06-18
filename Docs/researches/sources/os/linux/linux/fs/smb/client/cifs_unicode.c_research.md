# File Research: sources/os/linux/linux/fs/smb/client/cifs_unicode.c

CIFS local-codepage and UTF-16LE conversion implementation, including SMB reserved-character remapping.

Inbound conversion maps UTF-16LE server strings to the local NLS codepage through `cifs_from_utf16()`, using `cifs_mapchar()` to apply SFM/SFU reverse mappings, codepage conversion, UTF-8 surrogate/variation-sequence fallback, and `?` substitution for unknown characters.

Outbound conversion is handled by `cifs_strtoUTF16()` for direct conversion and `cifsConvertToUTF16()` when reserved-character remapping is requested. SFU maps POSIX-reserved characters to Unicode private/reserved values; SFM maps control characters and Mac-style private-use values, including end-of-component period/space handling while preserving `.` and `..`.

Length/allocation helpers include `cifs_utf16_bytes()`, `cifs_strndup_from_utf16()`, `cifs_local_to_utf16_bytes()`, and `cifs_strndup_to_utf16()`. The implementation uses unaligned little-endian access because SMB wire strings may not be naturally aligned.

Known constraints are documented in comments: slash/backslash remapping is avoided because path-building code treats those as separators.
