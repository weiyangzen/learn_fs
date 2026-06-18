# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcolor.c

Implements Ghostscript’s core simple device-color types and supporting serialization helpers.

- Defines standard device color type vectors:
  - `gx_dc_type_none`: unset/undefined color.
  - `gx_dc_type_null`: drawing has no visible effect.
  - `gx_dc_type_pure`: a concrete single `gx_color_index`.
- Provides black/white device color caching:
  - `gx_device_black`
  - `gx_device_white`
  - `gx_device_decache_colors`
- `gx_set_rop_no_source` prepares a RasterOp source representing black, using cached device black when possible.
- `gx_device_color_equal` dispatches through the color type’s `equal` method.
- Maps device color type pointers to compact indices for command-list serialization:
  - `gx_get_dc_type_index`
  - `gx_get_dc_type_from_index`
  - The table includes none, null, pure, binary halftone, colored halftone, and WTS. Pattern colors are intentionally excluded from command lists.
- Implements canonical phase methods:
  - `gx_dc_no_get_phase`
  - `gx_dc_ht_get_phase`
- `none` color methods mostly no-op, fail on invalid rendering, and serialize as zero bytes if redundant.
- `null` color methods always render no output and compare equal by type.
- `pure` color methods render via `fill_rectangle`, `copy_mono`, or `strip_copy_rop` depending on RasterOp/source/mask needs.
- `gx_dc_pure_write` and `gx_dc_pure_read` serialize/deserialize a pure `gx_color_index`.
- `gx_dc_pure_get_nonzero_comps` decodes a pure color and returns a component bit mask for overprint support.
- `gx_complete_halftone` finalizes a colored halftone `gx_device_color`, including plane mask.
- `gx_dc_default_fill_masked` scans a 1-bit mask into runs and fills rectangles through the active device color.
- `gx_dc_write_color` / `gx_dc_read_color` provide compact big-endian-ish color-index encoding for command lists, with `gx_no_color_index` encoded as single byte `0xff`.

Important invariants:
- Equality must be conservative because it gates cache reuse.
- Command lists cannot store raw type pointers; stable type indices are used.
- Color index encoding depends on `dev->color_info.depth`.
