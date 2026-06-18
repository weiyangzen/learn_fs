# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/support.c

## Purpose
Implements small support routines for the `ctx` minifilter sample, specifically allocation and freeing of `UNICODE_STRING` buffers.

## Functions
- `CtxAllocateUnicodeString`
  - Expects `String->MaximumLength` to already contain the requested allocation size.
  - Allocates a zeroed `PagedPool` buffer with `CTX_STRING_TAG`.
  - Sets `String->Length` to zero on success.
  - Returns `STATUS_INSUFFICIENT_RESOURCES` if allocation fails.

- `CtxFreeUnicodeString`
  - Frees `String->Buffer` with `CTX_STRING_TAG`.
  - Resets `Length`, `MaximumLength`, and `Buffer`.

## Implementation Details
- Both routines are pageable.
- The functions use SAL annotations to describe postconditions for `Length`, `MaximumLength`, and `Buffer`.
- Debug tracing reports failed allocation size.

## Dependencies
- Includes `pch.h`.
- Uses `CTX_STRING_TAG` from `CtxStruc.h`.

## Research Notes
These helpers rely on callers setting `MaximumLength` correctly before allocation. They are used throughout the context sample to store volume names and file names in instance, file, stream, and stream-handle contexts.
