# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icolor.h

Declares interpreter color remapping procedures for transfer functions and related caches.

Exports:
- stack slot counts for `zcolor_remap_one`
- `zcolor_remap_one`
- unsigned and signed remap finish routines
- `zcolor_reset_transfer`
- `zcolor_remap_color`

The comments note that special-form procedures may avoid scheduling work but still return `o_push_estack`.
