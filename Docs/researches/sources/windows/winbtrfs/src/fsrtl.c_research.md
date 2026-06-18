# File Research: sources/windows/winbtrfs/src/fsrtl.c

## Purpose

`fsrtl.c` provides a compatibility implementation of `FsRtlValidateReparsePointBuffer` for environments where the Vista+ FsRtl API is unavailable or not exported.

## Main Entry Point

- `compat_FsRtlValidateReparsePointBuffer(ULONG BufferLength, PREPARSE_DATA_BUFFER ReparseBuffer)`

It validates Windows reparse point buffer shape, length consistency, tag class, and selected Microsoft tag payloads.

## Behavior

- Rejects buffers smaller than `REPARSE_DATA_BUFFER_HEADER_SIZE` or larger than `MAXIMUM_REPARSE_DATA_BUFFER_SIZE`.
- Accepts either normal `REPARSE_DATA_BUFFER` sizing or GUID reparse buffer sizing if the `ReparseDataLength` matches exactly.
- Requires non-Microsoft tags to use GUID reparse buffers.
- Rejects null GUIDs for non-Microsoft GUID reparse buffers.
- Rejects GUID buffer use for mount-point and symlink tags.
- Validates Microsoft mount point buffers:
  - substitute name must begin at offset 0,
  - print name must follow the substitute string plus null,
  - total data length must match fields plus two null terminators.
- Validates Microsoft symlink buffers:
  - substitute and print lengths must be nonzero,
  - offsets and lengths must be even UTF-16 byte counts,
  - both strings must fit inside the provided data length.
- Accepts other non-reserved Microsoft tags without detailed payload validation.
- Returns `STATUS_IO_REPARSE_DATA_INVALID` for malformed payloads and `STATUS_IO_REPARSE_TAG_INVALID` for invalid tag classes.

## Helpers

- `IsNullGuid()`: checks for all-zero GUID.
- `IsEven()`: validates UTF-16 byte alignment.

## Dependencies

- Includes `ntifs.h` and `ntdef.h`.
- Uses Windows reparse constants/macros such as `IsReparseTagMicrosoft`, `IO_REPARSE_TAG_MOUNT_POINT`, and `IO_REPARSE_TAG_SYMLINK`.

## Research Notes

- Header comment identifies this as ReactOS-derived Vista+ FsRtl compatibility code under LGPL-2.1-or-later.
- The function is security-sensitive because reparse data can cross user/kernel and filesystem boundary paths.
- The implementation focuses on structural validation, not semantic target validation.
