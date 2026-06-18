# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/siinterp.c

Implements the `ImageInterpolateEncode` stream filter.

Key points:
- Defines an interpolation state that extends generic image-scale parameters with pixel sizes, row sizes, current/previous row buffers, DDA state, offsets, and dispatch case.
- Initialization computes bytes per input/output pixel, row widths, DDA mappings from output to input dimensions, and allocates two row buffers.
- Chooses optimized conversion cases for same-format, 8-to-8 scaling, 8-to-16 byte-to-fraction conversion, 16-to-8, and 16-to-16 conversions.
- Processing reads whole input rows into `cur`, emits repeated/scaled output rows according to the Y DDA, and selects source X positions with the X DDA.
- Component values are rescaled between input/output maximum values when bit depths or maxima differ.
- Release frees the row buffers.

Dependencies and interactions:
- Uses `sisparam.h` shared image scaling parameters, DDA helpers from `gxdda.h`, and fraction conversion from `gxfrac.h`.

Research relevance:
- This is the nearest-neighbor/interpolation-style image scaling stream, distinct from the smoother Mitchell scaler in `siscale.c`.
