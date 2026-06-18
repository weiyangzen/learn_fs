# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/transupp.c

Support library for `jpegtran`-style lossless JPEG transformations and optional marker copying. It is outside the core JPEG codec but uses `JPEG_INTERNALS` for coefficient-array helpers.

Transform implementation:

- `do_flip_h()` mirrors DCT blocks in place and negates odd-column coefficients.
- `do_flip_v()` writes to destination coefficient arrays and negates odd-row coefficients.
- `do_transpose()` transposes DCT coefficient blocks and swaps image axes.
- `do_rot_90()`, `do_rot_270()`, `do_rot_180()`, and `do_transverse()` implement compound rotations/transverse transpose directly over coefficient arrays, preserving untransformable edge blocks unless trimming is requested.

Public transform API:

- `jtransform_request_workspace()` decides how many components are processed, handles force-grayscale component reduction, and requests virtual coefficient arrays when a transform cannot be done in place.
- `jtransform_adjust_parameters()` applies force-grayscale color-space changes, transposes dimensions/sampling/quantization tables for axis-swapping transforms, trims partial iMCU edges when requested, and returns the coefficient array set that should be written.
- `jtransform_execute_transformation()` dispatches to the selected coefficient transform after `jpeg_write_coefficients()` has initialized destination component dimensions.

Marker-copy support:

- `jcopy_markers_setup()` requests saving COM markers or all APPn markers before header read.
- `jcopy_markers_execute()` writes saved markers to the output, skipping duplicate JFIF APP0 and Adobe APP14 markers already emitted by the encoder.

This file is sensitive to JPEG iMCU geometry, padding, sampling factors, and quantization-table orientation. Its logic is image-transform-specific, not filesystem-related.
