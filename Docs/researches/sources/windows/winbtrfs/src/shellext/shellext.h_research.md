# File Research: sources/windows/winbtrfs/src/shellext/shellext.h

## Purpose
Shared shell extension header providing Windows target definitions, NT API declarations, fallback structure definitions, Btrfs constants, RAII handle wrappers, and common helper/error declarations.

## Main Contents
- Windows target setup:
  - `WINVER` and `_WIN32_WINNT` set to Windows 10.
  - `ISOLATION_AWARE_ENABLED`, `STRSAFE_NO_DEPRECATE`.
- NTSTATUS constants used across shell extension code, including success, buffer overflow, EOF, not ready, cannot delete, and not found.
- Btrfs block/profile flags:
  - data/system/metadata and RAID profile flags including RAID1C3/RAID1C4.
- Btrfs inode type constants used by shell operations.
- `funcname` macro mapped to compiler-specific function name macro.
- NT native declarations:
  - `NtReadFile`, `NtSetEaFile`, `NtSetSecurityObject`, `NtFsControlFile`, `NtQueryInformationFile`, `NtSetInformationFile`, `NtQueryVolumeInformationFile`.
- Compatibility definitions for non-MSVC builds:
  - `DUPLICATE_EXTENTS_DATA`
  - integrity information buffers
- `REPARSE_DATA_BUFFER` definition and `SYMLINK_FLAG_RELATIVE`.

## Utility Classes
- `win_handle`: RAII wrapper using `CloseHandle`.
- `fff_handle`: RAII wrapper using `FindClose`.
- `nt_handle`: RAII wrapper using `NtClose`.
- `string_error`, `last_error`, `ntstatus_error`: exception types carrying formatted messages.
- `global_lock`: RAII wrapper around `GlobalLock`/`GlobalUnlock`.

## Shared Helpers Declared
- `format_size`
- `set_dpi_aware`
- `format_message`
- `format_ntstatus`
- `load_string`
- `wstring_sprintf`
- `command_line_to_args`
- `utf8_to_utf16`
- `error_message`

## Dependencies
Includes Windows/NT headers, C++ strings/vectors/stdint, and WinBtrfs headers `../btrfs.h` and `../btrfsioctl.h`.

## Notable Behavior
This header is the compatibility and convenience layer that lets the shell extension call lower-level NT APIs and WinBtrfs private FSCTLs while keeping most implementation files concise.
