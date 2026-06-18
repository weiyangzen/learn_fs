# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtx.c

## Role

`gshtx.c` implements a stand-alone high-level halftone object API for building, referencing, releasing, and installing multi-component halftones with spot, threshold, or explicit mask components.

This is rendering support, not filesystem code.

## Main Interfaces

- Constructors/component setters: `gs_ht_build`, `gs_ht_set_spot_comp`, `gs_ht_set_threshold_comp`, `gs_ht_set_mask_comp`.
- Lifetime: `gs_ht_reference`, `gs_ht_release`.
- Installer: `gs_ht_install`.
- Internal helpers: `check_ht`, `build_transfer_map`, `alloc_ht_order`, `build_component`, `free_order_array`, `create_mask_bits`, `create_mask_order`.

## Core Behavior

- `gs_ht_build` allocates a reference-counted Type 5/multiple halftone plus component array and installs a custom free procedure that frees the component array.
- Component setters fill unused slots with spot or threshold definitions and always provide a transfer closure, using identity transfer when none is supplied.
- `gs_ht_install` validates the object, allocates component orders and transfer maps, builds each order, creates small caches for non-default components, then delegates to `gx_ht_install`.
- Transfer maps are precomputed across `transfer_map_size` samples and clamp output to the `[0, 1]` frac range.
- Mask-defined halftones compare successive bitmap masks to generate whitening-order bits and level offsets.

## Notable Risks

- `comp2order` is a fixed 32-byte stack array with a comment saying it is ample; there is no visible check that `num_comps <= 32`.
- `gs_ht_release` uses `rc_decrement_only`; the actual free path relies on reference-count conventions and `free_comps`.
- Threshold and mask data are caller-owned by contract, so callers must keep them valid until installation consumes/builds the order.
- The mask-order path is intentionally described as “silly” and uses a slow two-pass diff of adjacent masks.
