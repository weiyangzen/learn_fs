# File Research: sources/local-fs/ntfs-3g/libntfs-3g/bitmap.c

## Scope

Provides low-level bitmap bit accessors and attribute-backed run set/clear helpers for NTFS bitmap attributes.

## API And Behavior

- `ntfs_bit_set()` sets or clears one bit in a byte-addressed bitmap and silently ignores NULL bitmap pointers or invalid bit values.
- `ntfs_bit_get()` returns a single bit value or `-1` for a NULL bitmap.
- `ntfs_bit_get_and_set()` atomically reads a bit and updates it when needed, returning `-1` for invalid inputs.
- `ntfs_bitmap_set_bits_in_run()` is the shared implementation for setting or clearing a run of bits in an `ntfs_attr`. It handles partial first and last bytes by reading existing bytes, writes up to 8 KiB windows, and loops until the requested run is updated.
- `ntfs_bitmap_set_run()` and `ntfs_bitmap_clear_run()` wrap the shared helper with tracing.

## State And Dependencies

The file uses `ntfs_attr_pread()` and `ntfs_attr_pwrite()` to modify bitmap attributes, with local heap buffers allocated through NTFS helpers. Bit numbering is little-endian within each byte: bit `n` maps to byte `n >> 3` and mask `1 << (n & 7)`.

## Risks And Invariants

No bounds checks are performed by the single-bit helpers. The run update path has known partial-I/O danger points: failed last-byte reads or window writes can leave bitmap metadata inconsistent, and comments explicitly note missing rollback. `count == 0` is accepted by argument validation but drives edge arithmetic through the shared helper, so callers should avoid relying on it as a no-op unless tested.
