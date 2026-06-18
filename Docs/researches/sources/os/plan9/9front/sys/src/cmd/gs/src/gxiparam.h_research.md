# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiparam.h

Internal definitions for implementors of Ghostscript image types and image enumerators.

Key contents:
- Defines `gx_image_type_t`, the virtual table for image parameter storage type, begin procedure, source-size procedure, stream put/get, release, and PostScript ImageType index.
- Declares common source-size and dummy serialization/release helpers.
- Declares generic pixel image stream serialization helpers and variable-length integer helpers.
- Defines `gx_image_enum_procs_t`, the virtual table for feeding plane data, ending an image, optional flushing, and optional wanted-plane negotiation.
- Defines the common prefix for all image enumerators: image type, procs, target device, unique id, plane counts/depths/widths.
- Declares common enumerator initialization and shared ImageType 1 procedures.

Notable dependencies:
- Ghostscript structure descriptors from `gsstype.h`.
- Device client types from `gxdevcli.h`.

Research notes:
- The `planes_wanted` contract is important for ImageType 3/3x, where mask and pixel planes may be requested in changing proportions.
- The enum common ID exists so banding machinery can distinguish simultaneous image enumerations.
