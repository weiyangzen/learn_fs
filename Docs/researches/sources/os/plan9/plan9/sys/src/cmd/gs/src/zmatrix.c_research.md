# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmatrix.c

PostScript matrix and coordinate-transform operators. It handles CTM manipulation (`concat`, `initmatrix`, `setmatrix`, `.setdefaultmatrix`) and matrix-valued operations (`currentmatrix`, `defaultmatrix`, `concatmatrix`, `invertmatrix`, `rotate`, `scale`, `translate`).

`read_matrix`/`write_matrix` are used to convert PostScript six-element arrays into `gs_matrix` values and back. `zconcat`, `zsetmatrix`, and `zsetdefaultmatrix` update graphics-state matrices. `zrotate`, `zscale`, and `ztranslate` construct transformation matrices and write them to the supplied matrix operand.

`common_transform` supports `transform`, `dtransform`, `itransform`, and `idtransform`, dispatching either through the graphics state CTM or directly through a matrix operand depending on operand count/type. The file is the interpreter binding for `gsmatrix.h` and `gscoord.h` matrix arithmetic.
