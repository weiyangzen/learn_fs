# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/error_private.h

## Purpose

Private Zstd/FSE/HUF error-code utilities. It encodes error enums into `size_t` return values and provides helpers for testing and forwarding errors.

## Main Components

- `ERR_STATIC` inline/static control.
- `ERR_enum` typedef to `ZSTD_ErrorCode`.
- `PREFIX(name)` and `ZSTD_ERROR(name)` error encoding.
- `ERROR(name)` macro.
- Helpers:
  - `ERR_isError`
  - `ERR_getErrorCode`
  - `ERR_getErrorString`
  - `ERR_getErrorName`
- Forwarding macros:
  - `CHECK_V_F`
  - `CHECK_F`

## Dependencies

- `<stddef.h>`
- `zstd_errors.h`

## Research Notes

- Errors are represented as negative enum values cast to `size_t`; `ERR_isError()` checks values above `ERROR(maxCode)`.
- The header is private and explicitly not intended as public API.
- Many FSE/HUF functions use `CHECK_F` and `CHECK_V_F`; changing these macros affects control flow broadly.
