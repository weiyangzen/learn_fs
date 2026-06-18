# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/transupp.h

External interface for `transupp.c`.

Defines:

- `TRANSFORMS_SUPPORTED`, defaulting transform support on.
- Short external-name aliases for constrained linkers.
- `JXFORM_CODE`: none, horizontal/vertical flip, transpose, transverse, and 90/180/270 degree rotations.
- `jpeg_transform_info`: caller options `transform`, `trim`, `force_grayscale`, plus internal `num_components` and `workspace_coef_arrays`.
- Transform lifecycle functions: `jtransform_request_workspace()`, `jtransform_adjust_parameters()`, and `jtransform_execute_transformation()`.
- `JCOPY_OPTION`: copy no optional markers, comments only, or all optional markers, with `JCOPYOPT_DEFAULT` set to comments.
- Marker-copy functions: `jcopy_markers_setup()` and `jcopy_markers_execute()`.

The header documents the iMCU edge-padding problem and why `trim` exists. Correct callers must invoke the functions at specific points in the libjpeg read/write coefficient pipeline.
