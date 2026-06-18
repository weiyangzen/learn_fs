# File Research: sources/windows/reactos/drivers/filesystems/btrfs/fsrtl.c

## Purpose

`fsrtl.c` provides a compatibility implementation of `compat_FsRtlValidateReparsePointBuffer`, a Vista+ FsRtl API used to validate Windows reparse point buffers. It is ReactOS kernel support code included in the Btrfs driver tree.

## Functions

`IsNullGuid` checks whether all fields of a GUID are zero.

`IsEven` checks whether a UTF-16 byte count or offset is even.

`compat_FsRtlValidateReparsePointBuffer` validates:
- Total buffer size against `REPARSE_DATA_BUFFER_HEADER_SIZE` and `MAXIMUM_REPARSE_DATA_BUFFER_SIZE`.
- Consistency between `ReparseDataLength` and either normal or GUID reparse buffer headers.
- Microsoft tag usage: normal `REPARSE_DATA_BUFFER` layout is reserved for Microsoft tags.
- GUID reparse buffers: non-Microsoft tags cannot have a null GUID, and mount-point/symlink Microsoft tags cannot be represented as GUID buffers.
- Mount point buffers: substitute name must be first, null-terminated, print name offset must follow substitute name plus null, and total data length must match the fields plus two null terminators.
- Symlink buffers: substitute and print names must be present, lengths and offsets must be even, and both strings must fit inside the supplied data.
- Other acceptable non-reserved Microsoft tags are accepted without deeper layout validation.

Invalid layouts return `STATUS_IO_REPARSE_DATA_INVALID`; invalid tags fall through to `STATUS_IO_REPARSE_TAG_INVALID`; valid buffers return `STATUS_SUCCESS`.

## Research Notes

This file is narrow validation glue. Its correctness matters because `fsctl.c` dispatches reparse-point FSCTLs, and malformed reparse buffers can cross user/kernel boundaries. The code is defensive about size arithmetic and tag layout but implements only the validation surface, not reparse storage itself.
