# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsovrc.c

Implements Ghostscript overprint/overprint-mode compositor support and forwarding device behavior.

Key behavior:
- Defines GC descriptor for `gs_overprint_t`.
- Implements variable-length little-endian base-128 encoding/decoding for `gx_color_index`, supporting potentially 64-bit color indices.
- `c_overprint_equal` compares compositor type and overprint parameters.
- `c_overprint_write` serializes overprint flags and, when needed, drawn component bits.
- `c_overprint_read` decodes serialized overprint parameters and constructs a compositor.
- Defines `gs_composite_overprint_type` with create/equal/write/read/clist update procs.
- `gs_create_overprint` allocates a reference-counted compositor, assigns ID, type, and params.
- `gs_is_overprint_compositor` checks compositor type.
- Defines `overprint_device_t`, a forwarding device with `drawn_comps` and `retain_mask`.
- Provides three proc tables:
  - no-overprint forwarding procs
  - generic overprint procs for non-separable/non-linear color encodings
  - separable overprint procs for separable linear encodings
- `swap_color_index` handles byte order for multi-byte color indices on little-endian hosts.
- `set_retain_mask` builds a per-bit retain mask from non-drawn components and device component masks.
- `check_drawn_comps` builds a component mask from nonzero mapped component values.
- `update_overprint_params` switches proc tables based on overprint parameters and target color model, computes process/spot drawn components, handles degenerate all-components-drawn case, and updates retain masks.
- `overprint_open_device` opens target and copies parameters.
- `overprint_put_params` forwards target parameter updates, decaches colors, and closes itself if target closes.
- `overprint_get_page_device` forwards page-device lookup to target.
- `overprint_create_compositor` updates existing overprint device params when given an overprint compositor; otherwise delegates to default compositor creation.
- `overprint_generic_fill_rectangle` delegates to `gx_overprint_generic_fill_rectangle`.
- `overprint_sep_fill_rectangle` swaps color index as needed and chooses optimized masked fill path based on depth.
- `fill_in_procs` completes proc tables once using a temporary forward device.
- `c_overprint_create_default_compositor` suppresses no-op overprint, initializes proc tables lazily, allocates an overprint forwarding device, copies target params, sets target, and applies overprint params.

Dependencies:
- Uses device/compositor infrastructure: `gxcomp.h`, `gxdevice.h`, `gsdevice.h`, `gxoprect.h`, `gxdcolor.h`, and `gxistate.h`.
- Uses `gs_next_ids` for compositor identity.
- Relies on lower-level overprint rectangle helpers from `gxoprect`.

Research notes:
- The comments describe some fill routines as stubs historically, but current functions delegate to `gx_overprint_*` helpers.
- The compositor is suppressed for no-op overprint and for degenerate cases where all components are drawn, avoiding unnecessary forwarding devices.
