# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/wcache_lib.h

## Purpose
Public header for the UDFS write-cache library implemented by `wcache_lib.cpp`.

## Main Contents
- Includes `platform.h`, and conditionally `env_spec_w32.h` for console builds.
- Defines callback types:
  - `PWRITE_BLOCK`
  - `PREAD_BLOCK`
  - `PWRITE_BLOCK_ASYNC`
  - `PREAD_BLOCK_ASYNC`
  - `PCHECK_BLOCK`
  - `PUPDATE_RELOC`
  - `PWC_ERROR_HANDLER`
- Defines block-state bits: `WCACHE_BLOCK_USED`, `WCACHE_BLOCK_ZERO`, `WCACHE_BLOCK_BAD`.
- Defines error context structure `WCACHE_ERROR_CONTEXT`.
- Defines cache entry, frame, and main `W_CACHE` structures.
- Defines cache modes:
  - `WCACHE_MODE_ROM`
  - `WCACHE_MODE_RW`
  - `WCACHE_MODE_R`
  - `WCACHE_MODE_RAM`
  - `WCACHE_MODE_EWR` planned but excluded by `WCACHE_MODE_MAX`
- Defines pointer/flag masks and cache flags such as whole-packet caching, no-compare, chained I/O, bad-block handling, and no-write-through.
- Declares public cache API functions for init, read, write, flush, purge, release, direct access, mode changes, relocation sync, discard, and flag mutation.
- Declares async completion callback `WCacheCompleteAsync__`.

## Dependencies and Interactions
- Exposes kernel-style types and synchronization fields, including `ERESOURCE`.
- Designed for inclusion from C++ while exporting C-compatible declarations via `extern "C"`.
- The `W_CACHE` struct is not opaque, so callers can inspect or mutate cache internals if they include this header.
