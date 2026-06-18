# File Research: sources/virtualization/libblockdev/src/plugins/swap.h

This public header defines the swap plugin API.

Public definitions:
- `BD_SWAP_ERROR` maps to `bd_swap_error_quark()`.
- `BDSwapError` includes technology unavailable, unknown state, activation failure, old swap format, suspend image, unknown swap format, page-size mismatch, invalid label, and invalid UUID.
- `BDSwapTech` has one technology, `BD_SWAP_TECH_SWAP`.
- `BDSwapTechMode` includes create, activate/deactivate, query, set label, and set UUID.

Exported functions:
- Lifecycle: `bd_swap_init()`, `bd_swap_close()`.
- Availability: `bd_swap_is_tech_avail()`.
- Operations: `bd_swap_mkswap()`, `bd_swap_swapon()`, `bd_swap_swapoff()`, `bd_swap_swapstatus()`, `bd_swap_set_label()`, `bd_swap_check_label()`, `bd_swap_set_uuid()`, `bd_swap_check_uuid()`.

Research relevance:
- The error enum numeric order is used by Python overrides to map specific swap activation failures into more granular exception classes.
