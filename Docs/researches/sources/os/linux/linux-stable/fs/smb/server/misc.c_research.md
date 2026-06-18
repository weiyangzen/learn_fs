# File Research: sources/os/linux/linux-stable/fs/smb/server/misc.c

This file implements general ksmbd utility routines for wildcard matching, path/name conversion, filename validation, share-name extraction, directory-entry name conversion, and NT time conversion.

Functions:
- `match_pattern()`
  - Case-insensitive wildcard matcher supporting `*` and `?`.
  - Returns true/false style values despite the comment saying zero means matched.
  - TODO notes missing DOS wildcard semantics for `DOS_DOT`, `DOS_QM`, and `DOS_STAR`.

- `is_char_allowed()`
  - Rejects ASCII control characters and Windows-disallowed wildcard/path characters: `?`, `"`, `<`, `>`, `|`, `*`.

- `ksmbd_validate_filename()`
  - Walks a filename and rejects disallowed characters with `-ENOENT`.

- `ksmbd_validate_stream_name()`
  - Rejects `/`, `:`, and `\` inside alternate data stream names.

- `parse_stream_name()`
  - Splits `filename` on `:` using `strsep`.
  - Extracts stream name and optional stream type.
  - Recognizes `$DATA` as `DATA_STREAM` and `$INDEX_ALLOCATION` as `DIR_STREAM`.
  - Mutates the input filename buffer.

- `convert_to_nt_pathname()`
  - Converts a kernel `struct path` into a share-relative Windows path.
  - Uses `d_path()`, verifies the absolute path has the configured share path prefix, strips that prefix, ensures share root reports as `/`, then converts `/` to `\`.
  - Returns allocated string or `ERR_PTR()`.

- `get_nlink()`
  - Returns `st->nlink`, subtracting one for directories.

- `ksmbd_conv_path_to_unix()`, `ksmbd_conv_path_to_windows()`
  - Replace `\` with `/`, or `/` with `\`.

- `ksmbd_strip_last_slash()`
  - Removes trailing `/` characters in place.

- `ksmbd_casefold_sharename()`
  - Allocates a `KSMBD_REQ_MAX_SHARE_NAME` buffer.
  - Uses Unicode casefolding when `CONFIG_UNICODE` and a unicode map are available.
  - Falls back to ASCII lowercasing and returns `ERR_PTR(-E2BIG)` on truncation.

- `ksmbd_extract_sharename()`
  - Extracts final component after the last `\` and casefolds it.

- `convert_to_unix_name()`
  - Allocates and returns `share->path` joined with the share-relative name.
  - Handles a leading slash in the requested name.

- `ksmbd_convert_dir_info_name()`
  - Converts a directory entry name to UTF-16 using `smbConvertToUTF16()`.
  - Allocates up to `min(4 * name_len, PATH_MAX)` bytes and appends a UTF-16 NUL.

- `ksmbd_NTtimeToUnix()`
  - Converts NT time, based on 1601-01-01 in 100 ns units, to `timespec64`.
  - Handles negative values separately for 32-bit division constraints.

- `ksmbd_UnixTimeToNT()`
  - Converts `timespec64` to NT time.

- `ksmbd_systime()`
  - Returns current wall-clock time in NT format.

Dependencies:
- Share configuration from `mgmt/share_config.h`.
- SMB charset conversion from `smb_common.h`.
- VFS path handling through `d_path()` and `struct path`.

Risk areas:
- `parse_stream_name()` assumes `strsep(&s_name, ":")` leaves a usable `s_name`; callers must only use it when a stream separator exists.
- `convert_to_nt_pathname()` uses a simple prefix comparison against `share->path`; correctness depends on canonical path handling before this helper is called.
- `ksmbd_convert_dir_info_name()` allocates `sz` bytes but writes two trailing NUL bytes at `conv[*conv_len]` and `conv[*conv_len + 1]`; callers depend on conversion length staying within the overallocated buffer.
- Wildcard matching intentionally does not implement full DOS wildcard semantics.
