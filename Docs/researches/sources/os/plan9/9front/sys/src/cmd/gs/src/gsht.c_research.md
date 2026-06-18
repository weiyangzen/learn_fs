# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht.c

## Role

`gsht.c` implements the core Ghostscript halftone and screen-installation machinery: `setscreen`, current screen queries, screen phase state, halftone-order allocation/construction/release, device-halftone installation, colorant-name resolution, and effective transfer-map selection.

This is rendering halftone infrastructure, not filesystem code.

## Main Interfaces

- Public/externally used entry points: `gs_setscreen`, `gs_currentscreen`, `gs_currentscreenlevels`, `gx_imager_setscreenphase`, `gs_setscreenphase`, `gs_currentscreenphase_pis`, `gs_currentscreenphase`, `gs_currenthalftone`, `gx_ht_process_screen_memory`, `gx_ht_alloc_ht_order`, `gx_ht_alloc_order`, `gx_ht_alloc_threshold_order`, `gx_ht_alloc_client_order`, `gx_sort_ht_order`, `gx_ht_construct_spot_order`, `gx_ht_construct_bit`, `gx_ht_construct_bits`, `gx_ht_order_release`, `gx_device_halftone_release`, `gs_color_name_component_number`, `gs_cname_to_colorant_number`, `gx_imager_dev_ht_install`, `gx_ht_install`, `gx_imager_set_effective_xfer`, and `gx_set_effective_transfer`.
- Registers GC descriptors for `gx_ht_order`, `gs_halftone`, and `gx_device_halftone` and handles conditional pointer enumeration for threshold strings, client data, transfer closures, component arrays, cached tiles, and transfer maps.

## Core Behavior

- `gs_setscreen` samples a `gs_screen_halftone` through a `gs_screen_enum`, then installs it as a device halftone.
- Halftone orders own width/height/raster/shift geometry, levels arrays, bit-order arrays, optional tile caches, optional WTS screens, and optional transfer maps.
- Spot-function orders are sorted by sampled mask values, then expanded into bitmap offsets/masks through `gx_ht_construct_spot_order` and `gx_ht_construct_bits`.
- Threshold/client orders use caller-specified dimensions and threshold data but reuse the same low-level order/cache representation.
- `gx_imager_dev_ht_install` is the central ownership-transfer path. It maps operand halftone components onto device process components, fills missing components from the default order, creates tile caches for non-WTS orders, builds WTS screens from enumerators, computes LCM tile dimensions, and replaces or unshares the imager state's `dev_ht`.
- Colorant resolution treats `Default` specially and maps RGB-style color screen names to CMYK-style device colorants where appropriate.
- Effective transfer maps are reset from `set_transfer` gray/RGB maps and then overridden per halftone component if a component order supplies a transfer map.

## Notable Risks

- Ownership rules are intentionally complex: the installer sometimes moves operand substructures, sometimes copies them, and clears source references only after a successful install. Incorrect caller cleanup would leak or double-free levels, bit data, caches, WTS structures, or transfer maps.
- A sentinel value in the `width` field (`ht_wts_suppress_release`) suppresses duplicate release of shared WTS screens; this is fragile and explicitly documented as a hack.
- Error cleanup in `gx_imager_dev_ht_install` appears suspicious: it releases orders only when `comp_number == -1`, which is the opposite of the usual “initialized component” check and deserves caution if this legacy path is modified.
- `gs_currentscreenlevels` assumes `pgs->dev_ht` and component entries are valid after consulting the current device's gray index.
- LCM width/height calculations saturate at `max_int`; callers should not rely on exact repeat dimensions for very large component cells.
