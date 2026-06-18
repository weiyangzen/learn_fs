# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevperm.c

## Role

`gdevperm.c` implements the `permute` printer device, a regression/testing device for DeviceN and unusual color-component layouts.

## Device Behavior

By default it behaves like a CMYK contone printer and outputs PPM. With `Permute=1`, it reports a six-component DeviceN model and stores colors as a permuted tuple roughly `(yellow, cyan, cyan2, magenta, zero, black)`, then converts back to RGB for PPM output.

## Main Functions

- `perm_print_page()` reads rendered component rows, unpermutes CMYK/CMY as needed, converts to RGB, and writes binary PPM.
- `perm_get_color_mapping_procs()` selects mapping tables for mode 0 or mode 1.
- `gray_cs_to_perm_cm_*()`, `rgb_cs_to_perm_cm_*()`, and `cmyk_cs_to_perm_cm_*()` map Ghostscript color spaces to the current permuted color model.
- `perm_get_color_comp_index()` resolves separation colorant names.
- `perm_encode_color()` and `perm_decode_color()` pack/unpack 8-bit components into `gx_color_index`.
- `perm_set_color_model()` switches between DeviceCMYK, DeviceCMY, and DeviceN component lists.
- `perm_get_params()` and `perm_put_params()` expose `Permute`, `Mode`, and separation names.

## Dependencies

Uses Ghostscript printer-device APIs, color conversion helpers from `gxdcconv.h`, parameter-list APIs, and standard PPM output through `FILE`.

## Risks And Invariants

- This is intentionally a test device; output should remain visually comparable across normal/permuted modes.
- `perm_print_page()` allocates `raw_line` and `cooked_line` but does not check allocation failures before use.
- Color model changes must update component count, depth, polarity, colorant names, and Ghostscript printer parameters consistently.
- Duplicate colorant names in DeviceN are intentional and test code paths that assume standard Gray/RGB/CMYK layouts.
