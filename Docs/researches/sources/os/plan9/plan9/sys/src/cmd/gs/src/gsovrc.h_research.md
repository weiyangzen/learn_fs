# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsovrc.h

Defines the public/internal interface for Ghostscript’s overprint compositor. The long file comment explains when overprint compositing is relevant for high-level devices, low-level devices, forwarding devices, accumulating devices, transparency devices, and pattern rendering.

Key definitions:
- `gs_overprint_params_t` / `struct gs_overprint_params_s`: tracks whether retained components exist, whether spot components are retained, and `drawn_comps` bitmask.
- `gs_overprint_t`: compositor object containing `gs_composite_common` plus overprint parameters.
- Structure descriptors: `private_st_gs_overprint_t`, `public_st_overprint_params_t`.
- Public functions: `gs_create_overprint`, `gs_is_overprint_compositor`.

Integration:
- Includes `gsstype.h` and `gxcomp.h`.
- Used by pattern/color state code to update overprint behavior, notably Type 1/2 pattern set-color paths.
- The compositor is intended to wrap and follow the lifetime/open-close state of the underlying device.

Risk notes:
- `gs_overprint_clear_drawn_comp(drawn_comps, i)` clears `1 << 1` rather than `1 << i`; this looks like a historical typo with component-mask consequences.
- The model depends on device process-color mappings and assumes compositor installation/removal discipline elsewhere.
