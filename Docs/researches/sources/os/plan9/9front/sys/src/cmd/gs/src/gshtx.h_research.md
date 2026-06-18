# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtx.h

## Role

`gshtx.h` declares the stand-alone halftone/transfer object API implemented by `gshtx.c`.

This is graphics API infrastructure, not filesystem code.

## Main Declarations

- Aliases `gs_ht`, `gs_spot_ht`, `gs_threshold_ht`, `gs_ht_component`, and `gs_multiple_ht` onto existing Ghostscript halftone structs.
- `gs_ht_transfer_proc` as a closure-capable transfer callback.
- `gs_ht_build`, `gs_ht_set_spot_comp`, `gs_ht_set_threshold_comp`, `gs_ht_set_mask_comp`, `gs_ht_reference`, `gs_ht_release`, `gs_ht_install`.
- Assignment/reference macros `gs_ht_assign` and `gs_ht_init_ptr`.

## Important Contract

Construction is two-step: allocate the multi-component halftone, then initialize each component. Releasing a halftone does not release client data supplied to transfer callbacks or mask/threshold definitions.

## Notable Risks

The object is nominally opaque but implemented as aliases over concrete Ghostscript halftone structs, so ABI and ownership behavior follow the underlying halftone internals.
