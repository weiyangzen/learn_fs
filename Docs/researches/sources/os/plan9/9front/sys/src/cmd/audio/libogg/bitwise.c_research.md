# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libogg/bitwise.c

## Role

This is the libogg bit packing implementation vendored into 9front's audio command tree. It implements variable-width bitstream read/write operations over `oggpack_buffer`, in both least-significant-bit-first (`oggpack_*`) and most-significant-bit-first (`oggpackB_*`) variants.

This is codec/container infrastructure rather than filesystem code, but it is in scope through the included 9front source tree.

## Main Interfaces

The file implements the bitstream API declared in `ogg/ogg.h`:

- Write lifecycle: `oggpack_writeinit`, `oggpack_writecheck`, `oggpack_writetrunc`, `oggpack_writealign`, `oggpack_writecopy`, `oggpack_reset`, `oggpack_writeclear`.
- Read lifecycle: `oggpack_readinit`, `oggpack_look`, `oggpack_look1`, `oggpack_adv`, `oggpack_adv1`, `oggpack_read`, `oggpack_read1`.
- Position/buffer access: `oggpack_bytes`, `oggpack_bits`, `oggpack_get_buffer`.
- MSB-first mirrors: `oggpackB_*`.

The `mask[]` table provides bit masks from 0 to 32 bits; `mask8B[]` supports MSB truncation of partially filled bytes.

## Implementation Notes

`oggpack_write()` and `oggpackB_write()` accept up to 32 bits, expand storage in `BUFFER_INCREMENT` chunks, mask the input value, merge it into the current byte at `endbit`, and update `endbyte`, `endbit`, and `ptr`.

`oggpack_writecopy_helper()` supports copying arbitrary bit counts from a byte source. It uses direct `memmove` for byte-aligned copies and falls back to repeated 8-bit writes for unaligned copies. Trailing partial bytes are written with the selected bit order.

The read-side functions use `look` for non-advancing reads and `read` for advancing reads. On overflow or invalid bit counts they poison the buffer state by setting `ptr` to `NULL`, `endbyte` to `storage`, and `endbit` to `1`, then return `-1`.

## Error Handling and Risks

Allocation failures and oversized growth requests clear the write buffer with `oggpack_writeclear()`. Callers must treat a failed or cleared buffer as unusable until reinitialized.

The implementation relies on careful boundary checks before reading up to five bytes around `ptr`; these checks are central to avoiding overreads near the end of small buffers.

## Test Code

Under `_V_SELFTEST`, the file includes a large standalone test program covering:

- LSb and MSb packing.
- Fixed and inferred bit-width writes.
- Single-bit reads.
- Read-past-end behavior.
- Aligned and unaligned `writecopy` paths around allocation boundaries.
