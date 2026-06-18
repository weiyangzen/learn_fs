# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_unicode.c

## Purpose

Implements CIFS Unicode and local-codepage conversion helpers, including UTF-16LE wire-format conversion, SFU/SFM reserved-character remapping, surrogate-pair/IVS handling for UTF-8, and allocation helpers for converted strings.

## Main Responsibilities

- Converts reserved Unicode/private-use characters back to local characters:
  - `convert_sfu_char()` handles SFU mapchars for colon, asterisk, question, pipe, greater-than, and less-than.
  - `convert_sfm_char()` handles SFM private-use mappings, control characters, and special trailing space/period mappings.
- Converts UTF-16LE from server to local codepage:
  - `cifs_mapchar()` maps one UTF-16 character or UTF-8 surrogate/IVS sequence to local bytes, falling back to `?`.
  - `cifs_from_utf16()` converts a bounded UTF-16LE buffer into a null-terminated local string with overflow checks.
  - `cifs_utf16_bytes()` computes converted byte length excluding the null terminator.
  - `cifs_strndup_from_utf16()` allocates and converts server strings, or duplicates non-Unicode strings.
- Converts local strings to UTF-16LE wire format:
  - `cifs_strtoUTF16()` converts local strings using the supplied NLS table, with a UTF-8 fast path through `utf8s_to_utf16s()`.
  - `convert_to_sfu_char()` and `convert_to_sfm_char()` map local reserved characters to SFU/SFM Unicode values.
  - `cifsConvertToUTF16()` converts path strings to UTF-16LE while optionally applying SFU/SFM remapping and handling UTF-8 surrogate pairs/IVS.
  - `cifs_local_to_utf16_bytes()` computes required UTF-16 byte length.
  - `cifs_strndup_to_utf16()` allocates and converts local strings to null-terminated UTF-16LE.

## Key Data/Control Flow

- `cifs_from_utf16()` walks 16-bit words with unaligned little-endian reads and keeps a three-word lookahead for surrogate/IVS conversion.
- Destination overflow is avoided by switching to temporary conversion near the end of the output buffer and breaking before the null terminator would be overrun.
- UTF-8 surrogate/IVS support is only attempted when the active codepage name is `"utf8"`.
- `cifsConvertToUTF16()` treats SFM trailing space/period remapping per path component, while preserving special `.` and `..` symlink components.
- Slash/backslash remapping is explicitly not supported because path builders use separators internally.

## Integration Notes

- Uses CIFS mount flags through `cifs_remap()` in `cifs_unicode.h` to choose no remap, SFU remap, or SFM remap.
- Uses kernel NLS table callbacks `char2uni()` and `uni2char()`.
- Wire format is little-endian UTF-16 as required by SMB paths and names.

## Correctness and Risk Notes

- Conversion failures fall back to question mark rather than returning errors in most paths.
- `cifsConvertToUTF16()` allocates a small temporary UTF-16 buffer for UTF-8 surrogate handling; if unavailable, it falls back to `?`.
- `cifs_strndup_to_utf16()` sizes allocation using conversion byte count but calls conversion with `strlen(src)`, so callers must pass properly null-terminated strings.
