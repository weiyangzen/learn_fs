# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spdiff.c

PixelDifferenceEncode/Decode stream filters for component-wise horizontal differencing.

Key behavior:
- Initializes row byte count, trailing-bit mask, and a case-dispatch index based on `BitsPerComponent`, color count, and encode/decode mode.
- `s_PDiff_process` resets previous samples at row boundaries and handles encode/decode in one large switch.
- Supports 1-, 2-, 4-, 8-, and nominally 16-bit components, with specialized paths for common color counts and aligned/unaligned packing.
- Encoding computes current sample minus previous sample; decoding adds previous sample back.
- Preserves untouched trailing bits in the last row byte through `end_mask`.

Notable dependencies:
- State and defaults from `spdiffx.h`.

Research notes:
- The file is heavily macro-optimized and difficult to modify safely.
- The 16-bit component paths contain suspicious typos: `ENCODE16` writes `q[d] = t & 0xff` rather than using `ti`, and `DECODE16` writes `q[d] = s && 0xff`; the non-macro 16-bit decode path also uses `*++p >> 8` where a high-byte shift-left would be expected. These are high-risk areas if 16-bit pixel differencing is used.
