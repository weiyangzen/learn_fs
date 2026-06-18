# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_unicode.h

## Purpose

Declares CIFS Unicode conversion APIs and constants for SFM/SFU reserved-character remapping.

## Main Contents

- Defines SFM private-use code points for double quote, asterisk, question mark, colon, greater-than, less-than, pipe, slash, trailing space, and trailing period.
- Defines remap modes:
  - `NO_MAP_UNI_RSVD`
  - `SFM_MAP_UNI_RSVD`
  - `SFU_MAP_UNI_RSVD`
- Declares conversion helpers:
  - `cifs_from_utf16()`
  - `cifs_utf16_bytes()`
  - `cifs_strtoUTF16()`
  - `cifs_strndup_from_utf16()`
  - `cifsConvertToUTF16()`
  - `cifs_strndup_to_utf16()`
  - `cifs_toupper()`
- Defines `cifs_remap()` inline helper:
  - Returns SFM remap if `CIFS_MOUNT_MAP_SFM_CHR` is set.
  - Returns SFU remap if `CIFS_MOUNT_MAP_SPECIAL_CHR` is set.
  - Otherwise returns no remapping.

## Integration Notes

- Includes NLS and UCS2 utility headers.
- Ties path/name conversion behavior directly to CIFS superblock mount flags from `cifs_fs_sb.h`.
