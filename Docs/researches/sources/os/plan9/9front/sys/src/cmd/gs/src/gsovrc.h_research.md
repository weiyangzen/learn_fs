# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsovrc.h

Defines the Ghostscript overprint compositor interface. The extensive header comment documents how overprint/overprint mode interact with high-level devices, low-level rendering devices, forwarding devices, accumulating devices, transparency, pattern caches, and graphics-state lifetime.

Key structures:
- `gs_overprint_params_t`: holds retained/drawn component policy.
- `gs_overprint_t`: compositor object with `gs_composite_common` plus overprint parameters.

Public API:
- `gs_create_overprint(...)`: creates an overprint composite object.
- `gs_is_overprint_compositor(...)`: identifies overprint compositors.
- GC descriptors for overprint params/compositor.

Notable detail: `gs_overprint_clear_drawn_comp(drawn_comps, i)` clears `1 << 1` rather than `1 << i`, which looks suspicious and should be checked before relying on the macro.
