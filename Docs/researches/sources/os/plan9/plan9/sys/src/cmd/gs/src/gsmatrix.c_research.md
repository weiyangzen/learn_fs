# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmatrix.c

Implements matrix creation, arithmetic, coordinate transforms, fixed-point transforms, bounding-box transforms, and compact stream serialization.

Core APIs create identity, translation, scaling, and rotation matrices; multiply/invert/translate/scale/rotate matrices; transform points and distances forward or inverse; and transform bounding boxes by evaluating all four corners. Fast paths handle axis-aligned `xx/yy` and swapped `xy/yx` matrices.

Fixed-point support converts `gs_matrix` to `gs_matrix_fixed`, validates translation range, transforms points/distances into `gs_fixed_point`, and optionally provides rounded current-point transforms. Error paths return `undefinedresult` for non-invertible matrices and `limitcheck` for fixed overflow.

`sput_matrix` and `sget_matrix` serialize matrices with a compact control byte describing repeated/zero coefficients and optional float payloads, used by band-list/stream code.
