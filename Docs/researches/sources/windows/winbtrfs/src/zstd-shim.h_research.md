# File Research: sources/windows/winbtrfs/src/zstd-shim.h

## Purpose

`zstd-shim.h` provides a tiny compatibility shim for building Zstandard-related code in the WinBtrfs kernel environment.

## Contents

- Includes `stddef.h` and `stdint.h`.
- Defines local allocation hooks:
  - `ZSTD_malloc(size_t size)`
  - `ZSTD_calloc(size_t nmemb, size_t size)`
  - `ZSTD_free(void* ptr)`
- The allocation functions are stubs:
  - `ZSTD_malloc()` returns `NULL`.
  - `ZSTD_calloc()` returns `NULL`.
  - `ZSTD_free()` does nothing.
- Under `_MSC_VER`, includes `<crt/intrin.h>` and marks these intrinsics:
  - `_byteswap_uint64`
  - `_byteswap_ulong`
  - `_rotl`
  - `_rotl64`

## Relationship to Other Files

This header is meant to satisfy Zstd source expectations without pulling in normal C runtime allocation behavior. In a kernel driver, dynamic allocation needs to be explicit and controlled; returning `NULL` prevents accidental use of Zstd code paths that expect heap allocation through these hooks.

## Research Notes

The shim strongly suggests WinBtrfs uses Zstd routines in a restricted way where these allocation callbacks should not be reached, or where allocation-capable Zstd APIs are intentionally disabled. Any future Zstd integration that requires workspace allocation would need a real kernel-safe allocator instead of these stubs.
