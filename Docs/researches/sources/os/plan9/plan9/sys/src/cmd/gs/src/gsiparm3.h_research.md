# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm3.h

Defines ImageType 3 image parameters.

Key definitions:
- `gs_image3_interleave_type_t` with chunky, interleaved scan-line, and separate-source modes.
- `gs_image3_t`: pixel data dictionary, `InterleaveType`, and `MaskDict`.

Behavior notes:
- For `InterleaveType 3`, mask data source precedes pixel data sources.
- For interleave types 2 and 3, clients must provide mask data before the pixel data it masks; this is documented as not currently checked.

Exports descriptor macro and `gs_image3_t_init`.
