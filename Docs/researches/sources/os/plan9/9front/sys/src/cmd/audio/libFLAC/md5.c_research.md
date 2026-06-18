# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/md5.c

## Role

`md5.c` implements MD5 accumulation for libFLAC. FLAC uses MD5 as an audio stream integrity checksum, not as a security primitive. The file combines a public-domain MD5 transform with FLAC-specific formatting that converts decoded PCM sample arrays into the canonical little-endian byte stream before updating the digest.

## Major Functions

- `FLAC__MD5Transform()` is the core 64-step MD5 block transform over four 32-bit state words.
- `byteSwap()` and `byteSwapX16()` are big-endian helpers; on little-endian builds they compile to no-ops.
- `FLAC__MD5Update()` appends arbitrary bytes to the MD5 context, buffering partial 64-byte blocks.
- `FLAC__MD5Init()` initializes MD5 state and clears the reusable internal sample buffer.
- `FLAC__MD5Final()` pads the message, appends bit length, writes the 16-byte digest, frees the internal buffer, and zeroes the context.
- `format_input_()` interleaves per-channel FLAC integer samples into little-endian bytes for 1-, 2-, 3-, and 4-byte sample widths.
- `FLAC__MD5Accumulate()` sizes or grows the internal buffer, formats samples, and feeds them to `FLAC__MD5Update()`.

## Important Implementation Details

`format_input_()` special-cases common channel/sample-width combinations: 1, 2, 4, 6, and 8 channels for 1-, 2-, and 4-byte samples, plus common 3-byte mono/stereo cases. Other combinations fall back to general nested loops.

For 2- and 4-byte samples, it writes through `FLAC__int16 *` and `FLAC__int32 *` aliases and applies `H2LE_16` / `H2LE_32`. For 3-byte samples it writes bytes manually by shifting the signed 32-bit sample.

`FLAC__MD5Accumulate()` checks multiplication overflow before using the computed total size for allocation behavior. The initial `bytes_needed` expression is computed before the checks, but because it is `size_t`, wraparound is defined and the checked path returns `false` before the wrapped value is used for buffer growth.

## Risks / Edge Cases

- `bytes_per_sample` values outside 1..4 cause `format_input_()` to do nothing, but `FLAC__MD5Accumulate()` will still update MD5 with whatever is in the buffer. The caller is expected to supply valid FLAC sample sizes.
- The internal buffer is reused and only reallocated when capacity is too small. Failed `safe_realloc_()` is followed by `safe_malloc_()`, preserving a fallback allocation attempt.
- MD5 length tracking uses two 32-bit byte counters and writes a 64-bit bit length at finalization, matching MD5 expectations.
- `FLAC__MD5Final()` frees `ctx->internal_buf.p8` and zeroes the full context, so the context must be reinitialized before reuse.

## Dependencies

Uses `private/md5.h` for the context layout, `share/alloc.h` for safe allocation helpers, `share/compat.h`, and `share/endswap.h` for endian conversions.
