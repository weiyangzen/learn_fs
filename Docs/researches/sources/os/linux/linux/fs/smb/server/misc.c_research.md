# File Research: sources/os/linux/linux/fs/smb/server/misc.c

This file contains shared ksmbd utility routines for pattern matching, filename/path conversion, share-name case folding, directory-name conversion, and SMB/Unix time conversion.

Main behavior:
- `match_pattern()` implements case-insensitive wildcard matching with `*` and `?`. It explicitly notes missing DOS wildcard semantics for DOS_DOT, DOS_QM, and DOS_STAR.
- `ksmbd_validate_filename()` rejects ASCII control characters and Windows-invalid wildcard/special characters such as `?`, `"`, `<`, `>`, `|`, and `*`.
- `parse_stream_name()` splits NTFS alternate data stream syntax, validates stream names against `/`, `:`, and `\`, and maps `$DATA` to `DATA_STREAM` and `$INDEX_ALLOCATION` to `DIR_STREAM`.
- `convert_to_nt_pathname()` converts a kernel `struct path` to a share-relative Windows path after verifying it is under the share root.
- `convert_to_unix_name()` joins a share root and client-relative path into a Unix path string.
- `ksmbd_casefold_sharename()` uses Unicode casefolding when available, otherwise ASCII lowercasing.
- `ksmbd_extract_sharename()` extracts the final component of a UNC tree path.
- `ksmbd_convert_dir_info_name()` converts directory names to UTF-16 for SMB directory responses.
- `ksmbd_NTtimeToUnix()`, `ksmbd_UnixTimeToNT()`, and `ksmbd_systime()` convert between NTFS 100ns timestamps since 1601 and Unix `timespec64`.

Notable implementation details:
- Path conversion mutates slash direction with `strreplace`.
- `convert_to_nt_pathname()` returns `ERR_PTR` values on allocation, prefix, or `d_path()` failure.
- The NT time conversion handles negative pre-1970 timestamps without relying on signed 64-bit division on 32-bit architectures.
- `parse_stream_name()` assumes the caller passes a name containing stream syntax; callers should avoid invoking it on names where `strsep()` leaves no stream component.

Role in this group:
- Provides utility declarations in `misc.h`.
- Used by SMB request handlers and VFS-facing code for path, share, directory, and time normalization.
