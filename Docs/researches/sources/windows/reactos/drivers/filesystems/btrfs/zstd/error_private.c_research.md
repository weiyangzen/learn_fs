# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/error_private.c

## Purpose

Private error string implementation for Zstd/FSE/HUF error codes.

## Main Components

- `ERR_getErrorString(ERR_enum code)`

## Behavior

- If `ZSTD_STRIP_ERROR_STRINGS` is defined, always returns `"Error strings stripped"`.
- Otherwise maps `ZSTD_error_*` values to stable diagnostic strings for common failures:
  - corruption
  - wrong checksum
  - unsupported parameters
  - allocation failure
  - destination/source size errors
  - table/log/symbol bounds
  - dictionary errors
  - seekable I/O errors
- Returns `"Unspecified error code"` for unknown/default cases.

## Dependencies

- `error_private.h`
- `zstd_errors.h` through the header.

## Research Notes

- This file embeds all private error text in one translation unit.
- It is diagnostic support only; error encoding/decoding lives in `error_private.h`.
