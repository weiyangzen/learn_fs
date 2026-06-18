# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdpnext.c

Implements NeXT Display PostScript extensions.

Alpha operators: `currentalpha` and `setalpha`.

Imaging/compositing operators:
- `.alphaimage`
- `composite`
- `compositerect`
- `dissolve`

`begin_composite()` creates a `gs_composite_alpha` object and asks the current device to create a compositor device. `end_composite()` closes/frees the temporary compositor and restores the original device.

`composite_image()` builds a `gs_image2_t` source image from either current state or a supplied gstate, adjusts CTM around destination placement, and sends it to `process_non_source_image()`.

Image sizing helpers:
- `.sizeimagebox` transforms and clips a source rectangle to current device bounds.
- `.sizeimageparams` reports bits/sample, multiproc false, and number of color components.

`device_is_true_color()` tests whether gray/RGB/CMYK devices map component values directly into decomposed packed pixels.

Registered in `zdpnext_op_defs`.
