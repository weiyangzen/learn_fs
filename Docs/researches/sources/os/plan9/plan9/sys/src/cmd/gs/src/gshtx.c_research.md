# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtx.c

Provides a stand-alone high-level halftone/transfer object interface layered over Ghostscript’s regular halftone structures.

Main API implementation:
- `gs_ht_build`: allocates a multiple halftone and component array.
- `gs_ht_set_spot_comp`: defines a spot-function component.
- `gs_ht_set_threshold_comp`: defines a threshold-array component.
- `gs_ht_set_mask_comp`: defines a mask-sequence component using client-order callbacks.
- `gs_ht_reference`, `gs_ht_release`: reference-count wrapper operations.
- `gs_ht_install`: validates, builds component orders, allocates caches, and installs via `gx_ht_install`.

Transfer behavior:
- Missing transfer callbacks are replaced by `null_closure_transfer`.
- `build_transfer_map` samples transfer functions into `gx_transfer_map` entries.

Mask-order support:
- `create_mask_bits` compares consecutive masks and emits order bits where the mask changes.
- `create_mask_order` translates explicit masks into the order/levels representation expected by the halftone renderer.

Risks and quirks:
- `comp2order` is fixed at 32 bytes and assumes component counts fit.
- The stand-alone builder only validates spot and threshold components in `check_ht`, despite `gs_ht_set_mask_comp` producing client-order components; this mismatch is notable.
- Client data ownership remains with the caller.
