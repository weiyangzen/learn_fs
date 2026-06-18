# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiparam.h

Internal definitions for implementors of Ghostscript image types and image enumerators.

Key contents:
- Defines `gx_image_type_t`, the virtual table for image storage type, begin procedure, source-size procedure, stream put/get, release, and PostScript ImageType index.
- Declares common source-size and dummy serialization/release helpers.
- Declares generic pixel image stream serialization helpers and variable-length integer helpers.
- Defines `gx_image_enum_procs_t`, the virtual table for feeding plane data, ending an image, optional flushing, and optional plane-wanted negotiation.
- Defines the common prefix for all image enumerators, including image type, procs, target device, unique id, plane counts, plane depths, and plane widths.
- Declares common enumerator initialization and the shared ImageType 1 procedures used by ImageType 4.

Notable dependencies:
- Structure descriptor declarations from `gsstype.h`.
- Device client types from `gxdevcli.h`.

Research notes:
- The `planes_wanted` contract is central for ImageType 3/3x, where mask and pixel planes can be requested in changing proportions.
- The unique enumerator ID is intended for banding machinery that may track simultaneous image enumerations.
