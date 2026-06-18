# File Research: sources/windows/dokany/dokan_fuse/src/utils.cpp

## Role

Provides conversion utilities for the Dokan FUSE bridge: string encoding, path normalization, FILETIME/unix time conversion, NTSTATUS/errno mapping, and argument conversion.

## Main Functions

- Encoding:
  - `utf8_to_wchar_buf`
  - `utf8_to_wchar_buf_old`
  - `wchar_to_utf8_cstr`
- Paths:
  - `unixify`
  - `extract_file_name`
  - `extract_dir_name`
- Time:
  - `unixTimeToFiletime`
  - `filetimeToUnixTime`
  - `is_filetime_set`
- Errors:
  - `ntstatus_error_to_errno`
  - `errno_to_ntstatus_error`
- CLI argument conversion:
  - `convert_args`
  - `free_converted_args`

## Behavior

- Converts UTF-8 to UTF-16 using `MultiByteToWideChar(CP_UTF8)`.
- Treats replacement character `U+FFFD` as conversion failure.
- Falls back to ANSI codepage conversion in `utf8_to_wchar_buf_old`.
- Normalizes Windows backslashes to Unix slashes and removes trailing slash except for root.
- Maps common NTSTATUS values to POSIX errno values and back.
- Converts `wchar_t **argv` to heap-allocated UTF-8 `char **argv`.

## Dependencies

- Windows APIs:
  - `MultiByteToWideChar`
  - `WideCharToMultiByte`
  - `FILETIME`
- NTSTATUS constants.
- POSIX errno constants.

## Notes and Risks

- The NTSTATUS/errno mapping is limited and defaults unknown errors to `EINVAL` or `STATUS_NOT_IMPLEMENTED`.
- `wchar_to_utf8` allocates with `malloc`; callers must free through provided wrappers or equivalent.
- `utf8_to_wchar_buf_old` uses ACP fallback, which may be lossy but supports legacy filenames.
