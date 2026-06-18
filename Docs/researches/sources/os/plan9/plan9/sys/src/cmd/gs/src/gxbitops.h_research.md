# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitops.h

Purpose: Defines internal macros for efficient bitmap bit/chunk operations.

Key definitions:
- Chunk size/bit/alignment helpers: `cbytes`, `clog2_bytes`, `cbits`, `clog2_bits`, `cbit_mask`, `calign_bytes`, `calign_bit_mask`.
- Full-mask and high-bit mask helpers: `cmask`, `chi_bits`.
- `arch_cant_shift_full_chunk` for platforms unable to shift full-width longs.
- `inc_ptr()` byte-wise pointer arithmetic.
- Monobit mask setup macros: `set_mono_left_mask`, `set_mono_thin_mask`, `set_mono_right_mask`.
- `mono_copy_chunk` is `uint` on big-endian systems and `bits16` on little-endian systems.

Behavior:
- Assumes bits inside bytes and bytes in scanlines are stored big-endian for mono copy source data.
- Uses lookup tables on little-endian systems (`mono_copy_masks`, `mono_fill_masks`) and arithmetic masks on big-endian systems.
- Contains compiler-workaround macro definitions for older C compilers.

Dependencies:
- Includes `gsbitops.h` and relies on architecture macros.

Notable risks:
- Heavy macro use is sensitive to type width and shift semantics.
- Some macros only accept constrained argument ranges, as documented.
