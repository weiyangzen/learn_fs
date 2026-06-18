# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/transupp.h

Header for `jpegtran` support routines implemented in `transupp.c`.

Primary declarations:
- `JXFORM_CODE` enumerates supported transforms: none, horizontal/vertical flip, transpose, transverse, rotations 90/180/270.
- `jpeg_transform_info` stores caller options (`transform`, `trim`, `force_grayscale`) plus internal workspace metadata.
- `jtransform_request_workspace`, `jtransform_adjust_parameters`, and `jtransform_execute_transformation` define the three-stage transform protocol.
- `JCOPY_OPTION` enumerates optional marker-copy policies: none, comments, all.
- `jcopy_markers_setup` and `jcopy_markers_execute` define marker preservation setup/execution.

Important documentation:
- The header explains partial-iMCU asymmetry: JPEG padding exists on right/bottom edges but not top/left, so flips/rotations may expose padding unless trimming is used.
- It documents force-to-grayscale as lossless for YCbCr luminance but not a geometric transform.
- It warns that function timing relative to reading/writing source and destination JPEGs is strict.

Portability:
- `TRANSFORMS_SUPPORTED` can disable transform declarations.
- `NEED_SHORT_EXTERNAL_NAMES` maps long external symbols to short aliases for old linkers.

Filesystem relevance:
- Interface metadata only; no direct IO.
