# File Research: sources/os/linux/linux-stable/fs/erofs/decompressor_deflate.c

## Summary
Implements EROFS DEFLATE decompression using pooled zlib inflate streams, with optional crypto acceleration fallback.

## Main Responsibilities
- Configures and lazily allocates a stream pool.
- Validates DEFLATE config records.
- Waits for an available stream context.
- Streams input/output pages through `z_erofs_stream_switch_bufs()`.
- Returns stream contexts to the pool.

## Key APIs
- `z_erofs_deflate_decomp`

## Important Behavior
By default, the stream count is `num_possible_cpus()`. The software path uses raw DEFLATE via `zlib_inflateInit2(..., -MAX_WBITS)`. Non-partial requests try crypto acceleration first when enabled.

## Risks
Pool exhaustion blocks waiters. The in-kernel zlib path cannot customize window bits despite validating the on-disk field.
