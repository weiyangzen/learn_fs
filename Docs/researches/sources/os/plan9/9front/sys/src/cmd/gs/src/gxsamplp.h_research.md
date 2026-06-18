# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsamplp.h

Multi-include template header that generates sample unpacking functions for 1-, 2-, 4-, and 8-bit samples, with optional per-component lookup-map rotation.

Key behavior:
- Requires callers to define `MULTIPLE_MAPS` and the four `TEMPLATE_sample_unpack_*` function names before inclusion.
- For `MULTIPLE_MAPS`, `NEXT_MAP`/`NEXT_MAP8` advance through per-component `sample_map` tables modulo `num_components_per_plane`.
- 1-bit unpacking expands either by 4-bit chunks into `bits32` values when `spread == 1`, or by individual bits into byte output when spreading.
- 2-bit unpacking expands nibbles into `bits16` values for contiguous output or individual 2-bit samples into byte output.
- 4-bit unpacking maps high/low nibbles into byte output.
- 8-bit unpacking can avoid copying entirely when output is contiguous and the map is identity; otherwise it maps bytes into the destination buffer.
- Each routine updates `*pdata_x` to the residual sample offset appropriate for the bit depth.

Notable dependencies:
- Included by `gxsample.c`; depends on `sample_lookup_t`, `sample_map`, `byte`, `bits16`, and `bits32`.

Research notes:
- This is intentionally not guarded by a normal include guard because it is included multiple times in one translation unit.
- `dsize` is treated as source byte count; routines compute `left` after applying the sample offset.
