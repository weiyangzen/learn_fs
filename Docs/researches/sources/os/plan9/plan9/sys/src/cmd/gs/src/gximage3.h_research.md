# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage3.h

Internal API for Ghostscript ImageType 3 processing.

Key contents:
- Defines callback signatures for creating the mask image device and the mask clipping device/enumerator.
- Documents that ImageType 3 mask/pixel splitting is used both for actual imaging and for high-level output writers.
- Exports `gx_begin_image3_generic`, parameterized by mask-device and mask-clip setup callbacks.

Notable dependencies:
- `gsiparm3.h` for public ImageType 3 parameter structures.
- `gxiparam.h` for typed image and enumerator interfaces.

Research notes:
- This is a small virtualization layer for mask/pixel orchestration; clients can reuse splitting without using the default memory-mask clipping device.
