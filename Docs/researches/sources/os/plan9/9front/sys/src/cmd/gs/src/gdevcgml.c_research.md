# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgml.c

Implementation of the CGM-writing library used by `gdevcgm.c`. It serializes CGM binary commands, tracks metafile/picture/attribute state, and provides public functions for CGM elements.

Key behavior:
- `cgm_initialize` allocates and initializes `cgm_state` defaults for metafile, picture, control, and attribute elements.
- Public APIs emit CGM elements for metafile control, picture control, primitives, cell arrays, geometry, and drawing attributes.
- `begin_command`, `put_*`, `write_command`, and `end_command` implement binary command buffering with short and extended-length CGM command encoding.
- Integer, real, VDC, point, string, color, RGB, and byte-array encoders honor the current precision and color selection state.
- `cgm_CELL_ARRAY` writes packed cell data row by row, including source-bit shifting and even-byte padding.

Notable dependencies:
- Internal definitions from `gdevcgmx.h`.
- Standard memory/string/file wrappers.

Research notes:
- The implementation mostly trusts callers; invalid state/range handling is minimal despite result codes existing for such errors.
- Floating real representation is stubbed: `put_real` only implements fixed representation.
- In `cgm_set_metafile_elements`, the `cgm_set_COLOR_PRECISION` branch writes `meta->color_precision` but assigns `st->metafile.color_index_precision = meta->color_index_precision`; this looks like a copy/paste bug because it does not update `st->metafile.color_precision`.
