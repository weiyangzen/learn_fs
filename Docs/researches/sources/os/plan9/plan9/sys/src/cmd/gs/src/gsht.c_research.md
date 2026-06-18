# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht.c

Implements core Ghostscript halftone state operations: `setscreen`, screen phase management, current halftone queries, halftone order allocation/construction/release, device halftone installation, colorant name resolution, and effective transfer selection.

Key responsibilities:
- Defines GC descriptors for `gx_ht_order`, `gs_halftone`, and `gx_device_halftone`.
- Allocates halftone orders via `gx_ht_alloc_ht_order`, `gx_ht_alloc_order`, `gx_ht_alloc_threshold_order`, and `gx_ht_alloc_client_order`.
- Sorts sampled spot/threshold values and converts whitening order entries into bit offset/mask records.
- Handles release of halftone orders, caches, WTS screens, transfer maps, and per-component device halftones.
- Installs device halftones into an imager state with `gx_imager_dev_ht_install`, including component expansion, default-component handling, ownership transfer, WTS conversion, cache creation, and LCM tile sizing.
- Installs high-level halftones into `gs_state` with `gx_ht_install`.

Important design notes:
- The file contains extensive comments explaining the mismatch between operand halftones and installed imager halftones.
- Ownership is mixed: some order data is moved from the operand into the installed halftone when memory matches; otherwise it is copied.
- Transfer maps are reference-counted; order data and caches generally are not.
- WTS sharing uses a hack: `width == 0xffff` suppresses duplicate release of shared WTS screens.
- `gx_imager_set_effective_xfer` starts from current transfer maps and then applies halftone dictionary overrides per component.

Risks and quirks:
- Complex ownership rules make error paths and shared structures fragile.
- `gs_color_name_component_number` treats `Default` as `GX_DEVICE_COLOR_MAX_COMPONENTS` and remaps RGB names to CMYK names for colorscreen-style halftones.
- The WTS duplicate-release suppression relies on a field that is normally unused for WTS orders.
