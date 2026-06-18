# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse_decode.c

## Purpose
Implements the public LZFSE buffer decode wrapper around the internal streaming decoder state.

## Main Responsibilities
- Reports scratch size as `sizeof(lzfse_decoder_state)`.
- Initializes `lzfse_decoder_state` source/destination pointers.
- Invokes `lzfse_decode()` and maps internal status codes to public byte-count return values.
- Allocates temporary scratch memory with `kmalloc()` if the caller passes no scratch buffer.

## Key Functions
- `lzfse_decode_scratch_size()`
- `lzfse_decode_buffer_with_scratch()`
- `lzfse_decode_buffer()`

## Dependencies
Depends on `lzfse.h`, `lzfse_internal.h`, and Linux slab allocation.

## Notes
A failed decode returns `0`; a full destination returns `dst_size`, matching the upstream LZFSE API contract.
