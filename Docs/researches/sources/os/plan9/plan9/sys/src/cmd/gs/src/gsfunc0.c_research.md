# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc0.c

## Role

Implementation of FunctionType 0 sampled functions.

## Main Data

Defines `gs_function_Sd_t`, sample extraction routines for 1/2/4/8/12/16/24/32 bits, interpolation helpers, and a pole cache for cubic interpolation. Supports up to 16 inputs and 16 outputs.

## Control Flow

Initialization validates dimensions, Domain/Range, sample size, order, bit depth, and sample-table sizes, then optionally allocates `array_step`, `stream_step`, and pole cache arrays. Evaluation clamps/encodes inputs into sample-space coordinates, fetches packed sample values from `DataSource`, interpolates linearly or cubically, decodes/clamps outputs, and returns floats. Cubic evaluation can use a cached tensor of Bezier poles. Monotonicity support maps requested subdomains into sample-index space and tests lattice/tensor monotonicity for shading decomposition. The file also implements parameter writing, scaled-copy creation, parameter freeing, and serialization including sample data.

## Dependencies

Uses `gsfunc0.h`, data source support, function common helpers, Ghostscript parameter lists, floating helpers, and streams.

## Notes

Pole-cache logic is marked as temporary development technology by compile-time flags. Higher-dimensional monotonic tests are limited by small fixed arrays.
